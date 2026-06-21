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


def load_service_names(services_file: Path, *, model_dir: Path | None = None) -> set[str]:
    """Return the set of registered service names (registry).

    Uses recursive discovery when model_dir is provided, otherwise the single file.
    """
    if model_dir is not None and model_dir.exists():
        all_services, _groups, _errors = load_all_services(model_dir)
        return set(all_services.keys())

    if not services_file.exists():
        return set()
    with services_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return set((data.get("services") or {}).keys())


def validate_depends_on(services_file: Path, *, model_dir: Path | None = None) -> list[CheckResult]:
    """Ensure every service `depends_on` target exists in the registry."""
    results: list[CheckResult] = []

    if model_dir is not None and model_dir.exists():
        all_services, _groups, _errors = load_all_services(model_dir)
        entries = [(name, meta, meta.get("_file", services_file)) for name, meta in all_services.items()]
    elif services_file.exists():
        with services_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        entries = [(name, meta or {}, services_file) for name, meta in (data.get("services") or {}).items()]
    else:
        return results

    known = {name for name, _meta, _src in entries}
    for name, meta, src in entries:
        for target in (meta or {}).get("depends_on") or []:
            if target not in known:
                results.append(CheckResult(
                    Severity.ERROR,
                    f"Service '{name}' depends_on '{target}' which is not a registered service",
                    src,
                ))
    return results


def validate_problem_service_refs(
    inbox_dir: Path,
    services_file: Path,
    *,
    model_dir: Path | None = None,
    known: set[str] | None = None,
) -> list[CheckResult]:
    """Warn when a problem references a service that is not in the registry.

    Pass `known` to validate against a precomputed registry (e.g. the union of all
    partitions); otherwise the registry is loaded from services_file / model_dir.
    """
    results: list[CheckResult] = []

    if not inbox_dir.exists():
        return results

    if known is None:
        known = load_service_names(services_file, model_dir=model_dir)

    try:
        prob_files = discover_problem_files(inbox_dir)
    except ValueError as e:
        results.append(CheckResult(Severity.ERROR, str(e)))
        return results

    for prob_file in prob_files:
        with prob_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        for svc in data.get("services") or []:
            if svc not in known:
                results.append(CheckResult(
                    Severity.WARNING,
                    f"Problem '{data.get('id', '?')}' references unknown service '{svc}'",
                    prob_file,
                ))
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
