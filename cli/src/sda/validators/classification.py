"""
Classification label validation.

Structural shape (labels is a str->str map) is checked by yamale; here we validate
label *values* against the configured vocabulary:
- value outside a closed dimension's `values`  → error
- dimension declared without `values` (open)   → any value accepted
- label using a dimension not declared at all   → warning

Covers all labelable entities: problems, services, ADRs, and partitions/systems.
"""

import yaml
from pathlib import Path

from sda.validators import CheckResult, Severity
from sda.validators.adr import get_labels as get_adr_labels
from sda.discovery import discover_problem_files, load_all_services, load_partition_labels
from sda.classification import load_dimensions

ADR_TEMPLATE = "TEMPLATE.md"


def _check(labels: dict | None, dimensions: dict, source: Path | None, who: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    for dim, value in (labels or {}).items():
        if dim not in dimensions:
            results.append(CheckResult(Severity.WARNING, f"{who} uses unknown classification dimension '{dim}'", source))
            continue
        allowed = dimensions[dim].get("values")
        if allowed is not None and value not in allowed:
            results.append(CheckResult(
                Severity.ERROR,
                f"{who} label {dim}='{value}' is not in allowed values {allowed}",
                source,
            ))
    return results


def validate_labels(
    project_dir: Path,
    inbox_dir: Path,
    model_dirs: list[Path],
    adr_dirs: list[Path],
    partition_paths: list[Path],
) -> list[CheckResult]:
    """Validate classification labels across problems, services, ADRs, and partitions."""
    dimensions = load_dimensions(project_dir)
    results: list[CheckResult] = []

    # Problems
    if inbox_dir.exists():
        try:
            prob_files = discover_problem_files(inbox_dir)
        except ValueError as e:
            return [CheckResult(Severity.ERROR, str(e))]
        for f in prob_files:
            with f.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            results += _check(data.get("labels"), dimensions, f, f"Problem '{data.get('id', '?')}'")

    # Services
    for md in model_dirs:
        if md.exists():
            all_services, _groups, _errs = load_all_services(md)
            for name, meta in all_services.items():
                results += _check(meta.get("labels"), dimensions, meta.get("_file"), f"Service '{name}'")

    # ADRs
    for ad in adr_dirs:
        if ad.exists():
            for f in sorted(ad.glob("*.md")):
                if f.name == ADR_TEMPLATE:
                    continue
                results += _check(get_adr_labels(f.read_text(encoding="utf-8")), dimensions, f, f"ADR '{f.stem.upper()}'")

    # Partitions / systems
    for pp in partition_paths:
        results += _check(load_partition_labels(pp), dimensions, pp / "partition.yaml", f"Partition '{pp.name}'")

    return results
