"""
Service model and staleness validators.

Checks:
- Services have last_reviewed and owner fields
- Services not reviewed within STALE_AFTER_DAYS are flagged
- Draft inbox problems overdue for triage are flagged
"""

import yaml
from datetime import date
from pathlib import Path

from sda.validators import CheckResult, Severity
from sda.discovery import discover_problem_files, discover_service_files, load_all_services

STALE_AFTER_DAYS = 180
TEMPLATE_FILENAME = "PROB-TEMPLATE.yaml"


def _validate_service_entries(services: dict, source_file: Path, today: date) -> list[CheckResult]:
    """Validate individual service entries for owner and staleness."""
    results: list[CheckResult] = []
    for name, meta in services.items():
        meta = meta or {}

        if "owner" not in meta:
            results.append(CheckResult(Severity.WARNING, f"Service '{name}' has no owner", source_file))

        if "last_reviewed" not in meta:
            results.append(CheckResult(Severity.WARNING, f"MISSING last_reviewed: {name}", source_file))
            continue

        try:
            reviewed = date.fromisoformat(str(meta["last_reviewed"]))
        except ValueError:
            results.append(CheckResult(
                Severity.ERROR,
                f"Invalid last_reviewed format for '{name}': {meta['last_reviewed']}",
                source_file,
            ))
            continue

        age = (today - reviewed).days
        if age > STALE_AFTER_DAYS:
            results.append(CheckResult(
                Severity.WARNING,
                f"STALE ({age}d): '{name}' — last reviewed {meta['last_reviewed']}",
                source_file,
            ))
    return results


def validate_services(services_file: Path, *, model_dir: Path | None = None) -> list[CheckResult]:
    """Check service entries for missing or stale last_reviewed fields.

    If model_dir is provided, recursively discovers all services.yaml files.
    Otherwise falls back to the single services_file.
    """
    results: list[CheckResult] = []
    today = date.today()

    if model_dir is not None and model_dir.exists():
        # Recursive discovery
        all_services, _groups, errors = load_all_services(model_dir)
        for err in errors:
            results.append(CheckResult(Severity.ERROR, err))

        # Group by source file for per-file validation
        files_seen: dict[Path, dict] = {}
        for name, meta in all_services.items():
            src = meta.pop("_file", services_file)
            meta.pop("_group", None)
            files_seen.setdefault(src, {})[name] = meta

        for src, svcs in files_seen.items():
            results.extend(_validate_service_entries(svcs, src, today))
        return results

    # Single-file fallback
    if not services_file.exists():
        results.append(CheckResult(Severity.WARNING, f"services.yaml not found at {services_file}"))
        return results

    with services_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    results.extend(_validate_service_entries(data.get("services") or {}, services_file, today))
    return results


def validate_draft_problems(inbox_dir: Path, sla_hours: int = 48) -> list[CheckResult]:
    """Flag draft inbox problems that exceed the triage SLA."""
    results: list[CheckResult] = []

    if not inbox_dir.exists():
        return results

    try:
        prob_files = discover_problem_files(inbox_dir)
    except ValueError as e:
        results.append(CheckResult(Severity.ERROR, str(e)))
        return results

    today = date.today()
    for prob_file in prob_files:
        with prob_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        if data.get("status") != "draft":
            continue

        created_at = data.get("created_at")
        if not created_at:
            results.append(CheckResult(Severity.WARNING, "Draft problem has no created_at", prob_file))
            continue

        try:
            created = date.fromisoformat(str(created_at))
        except ValueError:
            results.append(CheckResult(Severity.WARNING, f"Invalid created_at: {created_at}", prob_file))
            continue

        age_hours = (today - created).days * 24
        if age_hours > sla_hours:
            results.append(CheckResult(
                Severity.WARNING,
                f"DRAFT OVERDUE ({(today - created).days}d, SLA={sla_hours}h): '{data.get('title', '?')}'",
                prob_file,
            ))

    return results
