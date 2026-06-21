"""
sda check — run all SDA validators.

Usage:
  sda check            # run all checks, warn on issues
  sda check --strict   # exit non-zero on any error
  sda check --verbose  # show passed checks too
"""

import yaml
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from sda.discovery import ARCH_DIR, discover_partitions, discover_problem_files
from sda.validators import CheckResult, Severity, errors, warnings
from sda.validators.adr import validate_adrs, validate_adr_service_refs, validate_adr_service_existence
from sda.validators.services import (
    validate_services,
    validate_draft_problems,
    validate_depends_on,
    validate_problem_service_refs,
    load_service_names,
)
from sda.validators.owners import validate_owners, validate_domain_coverage, get_triage_sla
from sda.validators.classification import validate_labels

console = Console()

ADR_DIR = Path("architecture/adr")
INBOX_DIR = Path("architecture/inbox")
MODEL_DIR = Path("architecture/model")
SERVICES_FILE = Path("architecture/model/services.yaml")
OWNERS_FILE = Path("OWNERS.yaml")


def _icon(result: CheckResult) -> str:
    if result.severity == Severity.ERROR:
        return "[red]✗[/red]"
    if result.severity == Severity.WARNING:
        return "[yellow]⚠[/yellow]"
    return "[green]✓[/green]"


def _validate_system_fields(inbox_dir: Path, partition_names: set[str]) -> list[CheckResult]:
    """Validate system: field on all inbox problems when partitions exist."""
    results: list[CheckResult] = []
    if not inbox_dir.exists():
        return results

    try:
        prob_files = discover_problem_files(inbox_dir)
    except ValueError as e:
        results.append(CheckResult(Severity.ERROR, str(e)))
        return results

    for prob_file in prob_files:
        with prob_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        system = data.get("system")
        if not system:
            results.append(CheckResult(
                Severity.WARNING,
                f"Problem '{data.get('id', '?')}' has no system: field (partitions exist)",
                prob_file,
            ))
        elif system not in partition_names:
            results.append(CheckResult(
                Severity.WARNING,
                f"Problem '{data.get('id', '?')}' has system: '{system}' which doesn't match any partition ({', '.join(sorted(partition_names))})",
                prob_file,
            ))

    return results


def check(
    strict: Annotated[bool, typer.Option("--strict", help="Exit code 1 on any error")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show passed checks")] = False,
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Run all SDA validators — ADR lifecycle, service staleness, ownership coverage."""
    pd = project_dir
    sla = get_triage_sla(pd / OWNERS_FILE)
    arch_dir = pd / ARCH_DIR
    partitions = discover_partitions(arch_dir)

    if partitions:
        checks = _partitioned_checks(pd, arch_dir, partitions, sla)
    else:
        checks = _flat_checks(pd, sla)

    all_results: list[CheckResult] = []
    for _, results in checks:
        all_results.extend(results)

    all_errors = errors(all_results)
    all_warnings = warnings(all_results)

    # Display results grouped by check
    for name, results in checks:
        if not results and not verbose:
            continue
        if not results:
            rprint(f"[green]✓[/green] {name}")
            continue
        rprint(f"\n[bold]{name}[/bold]")
        for r in results:
            loc = f" [dim]{r.file.name}[/dim]" if r.file else ""
            rprint(f"  {_icon(r)}{loc} {r.message}")

    # Summary
    rprint()
    if not all_errors and not all_warnings:
        rprint("[green bold]✓ All checks passed[/green bold]")
    else:
        if all_errors:
            rprint(f"[red bold]{len(all_errors)} error(s)[/red bold]  [yellow]{len(all_warnings)} warning(s)[/yellow]")
        else:
            rprint(f"[green]✓ No errors[/green]  [yellow]{len(all_warnings)} warning(s)[/yellow]")

    if strict and all_errors:
        raise typer.Exit(1)


def _flat_checks(pd: Path, sla: int) -> list[tuple[str, list[CheckResult]]]:
    """Original flat-mode check list."""
    return [
        ("ADR Lifecycle", validate_adrs(pd / ADR_DIR)),
        ("ADR → Service refs", validate_adr_service_refs(pd / ADR_DIR, pd / SERVICES_FILE)),
        ("ADR service existence", validate_adr_service_existence(pd / ADR_DIR, pd / SERVICES_FILE, model_dir=pd / MODEL_DIR)),
        ("Service staleness", validate_services(pd / SERVICES_FILE, model_dir=pd / MODEL_DIR)),
        ("Service dependencies", validate_depends_on(pd / SERVICES_FILE, model_dir=pd / MODEL_DIR)),
        ("Problem service refs", validate_problem_service_refs(pd / INBOX_DIR, pd / SERVICES_FILE, model_dir=pd / MODEL_DIR)),
        ("Classification labels", validate_labels(pd, pd / INBOX_DIR, [pd / MODEL_DIR], [pd / ADR_DIR], [])),
        ("Draft problem SLA", validate_draft_problems(pd / INBOX_DIR, sla_hours=sla)),
        ("OWNERS.yaml", validate_owners(pd / OWNERS_FILE)),
        ("Domain coverage", validate_domain_coverage(pd / OWNERS_FILE, pd / SERVICES_FILE, model_dir=pd / MODEL_DIR)),
    ]


def _partitioned_checks(
    pd: Path,
    arch_dir: Path,
    partitions: list[tuple[str, Path]],
    sla: int,
) -> list[tuple[str, list[CheckResult]]]:
    """Build check list for partitioned layout."""
    checks: list[tuple[str, list[CheckResult]]] = []
    partition_names = {name for name, _ in partitions}

    # Root-level ADRs
    root_adr = pd / ADR_DIR
    if root_adr.exists():
        checks.append(("Root ADR Lifecycle", validate_adrs(root_adr)))

    # Per-partition checks
    for name, part_path in partitions:
        part_adr = part_path / "adr"
        part_model = part_path / "model"
        part_services = part_model / "services.yaml"
        label = f"\\[{name}]"

        if part_adr.exists():
            checks.append((f"{label} ADR Lifecycle", validate_adrs(part_adr)))
            checks.append((f"{label} ADR → Service refs", validate_adr_service_refs(part_adr, part_services)))
            checks.append((f"{label} ADR service existence", validate_adr_service_existence(part_adr, part_services, model_dir=part_model)))

        if part_model.exists():
            checks.append((f"{label} Service staleness", validate_services(part_services, model_dir=part_model)))
            checks.append((f"{label} Service dependencies", validate_depends_on(part_services, model_dir=part_model)))

    # system: field validation
    checks.append(("Problem system: field", _validate_system_fields(pd / INBOX_DIR, partition_names)))
    # Classification labels across problems, services, ADRs, and partitions
    part_models = [p / "model" for _, p in partitions]
    adr_dirs = [pd / ADR_DIR] + [p / "adr" for _, p in partitions]
    part_paths = [p for _, p in partitions]
    checks.append(("Classification labels", validate_labels(pd, pd / INBOX_DIR, part_models, adr_dirs, part_paths)))

    # Cross-cutting checks
    union_services: set[str] = set()
    for _name, part_path in partitions:
        union_services |= load_service_names(part_path / "model" / "services.yaml", model_dir=part_path / "model")
    checks.append(("Problem service refs", validate_problem_service_refs(pd / INBOX_DIR, pd / SERVICES_FILE, known=union_services)))
    checks.append(("Draft problem SLA", validate_draft_problems(pd / INBOX_DIR, sla_hours=sla)))
    checks.append(("OWNERS.yaml", validate_owners(pd / OWNERS_FILE)))

    return checks
