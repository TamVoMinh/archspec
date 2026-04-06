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

STALE_AFTER_DAYS = 180
TEMPLATE_FILENAME = "PROB-TEMPLATE.yaml"


def validate_services(services_file: Path) -> list[CheckResult]:
    """Check service entries for missing or stale last_reviewed fields."""
    results: list[CheckResult] = []

    if not services_file.exists():
        results.append(CheckResult(Severity.WARNING, f"services.yaml not found at {services_file}"))
        return results

    with services_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    today = date.today()
    for name, meta in (data.get("services") or {}).items():
        meta = meta or {}

        if "owner" not in meta:
            results.append(CheckResult(Severity.WARNING, f"Service '{name}' has no owner", services_file))

        if "last_reviewed" not in meta:
            results.append(CheckResult(Severity.WARNING, f"MISSING last_reviewed: {name}", services_file))
            continue

        try:
            reviewed = date.fromisoformat(str(meta["last_reviewed"]))
        except ValueError:
            results.append(CheckResult(
                Severity.ERROR,
                f"Invalid last_reviewed format for '{name}': {meta['last_reviewed']}",
                services_file,
            ))
            continue

        age = (today - reviewed).days
        if age > STALE_AFTER_DAYS:
            results.append(CheckResult(
                Severity.WARNING,
                f"STALE ({age}d): '{name}' — last reviewed {meta['last_reviewed']}",
                services_file,
            ))

    return results


def validate_draft_problems(inbox_dir: Path, sla_hours: int = 48) -> list[CheckResult]:
    """Flag draft inbox problems that exceed the triage SLA."""
    results: list[CheckResult] = []

    if not inbox_dir.exists():
        return results

    today = date.today()
    for prob_file in sorted(inbox_dir.glob("PROB-[0-9]*.yaml")):
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
