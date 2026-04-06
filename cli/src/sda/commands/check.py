"""
sda check — run all SDA validators.

Usage:
  sda check            # run all checks, warn on issues
  sda check --strict   # exit non-zero on any error
  sda check --verbose  # show passed checks too
"""

from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from sda.validators import CheckResult, Severity, errors, warnings
from sda.validators.adr import validate_adrs, validate_adr_service_refs
from sda.validators.services import validate_services, validate_draft_problems
from sda.validators.owners import validate_owners, validate_domain_coverage, get_triage_sla

console = Console()

ADR_DIR = Path("architecture/adr")
INBOX_DIR = Path("architecture/inbox")
SERVICES_FILE = Path("architecture/model/services.yaml")
OWNERS_FILE = Path("OWNERS.yaml")


def _icon(result: CheckResult) -> str:
    if result.severity == Severity.ERROR:
        return "[red]✗[/red]"
    if result.severity == Severity.WARNING:
        return "[yellow]⚠[/yellow]"
    return "[green]✓[/green]"


def check(
    strict: Annotated[bool, typer.Option("--strict", help="Exit code 1 on any error")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show passed checks")] = False,
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Run all SDA validators — ADR lifecycle, service staleness, ownership coverage."""
    pd = project_dir
    sla = get_triage_sla(pd / OWNERS_FILE)

    checks: list[tuple[str, list[CheckResult]]] = [
        ("ADR Lifecycle", validate_adrs(pd / ADR_DIR)),
        ("ADR → Service refs", validate_adr_service_refs(pd / ADR_DIR, pd / SERVICES_FILE)),
        ("Service staleness", validate_services(pd / SERVICES_FILE)),
        ("Draft problem SLA", validate_draft_problems(pd / INBOX_DIR, sla_hours=sla)),
        ("OWNERS.yaml", validate_owners(pd / OWNERS_FILE)),
        ("Domain coverage", validate_domain_coverage(pd / OWNERS_FILE, pd / SERVICES_FILE)),
    ]

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
