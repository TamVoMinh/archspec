"""
OWNERS.yaml validators.

Checks:
- OWNERS.yaml exists
- Required sections are present
- All services in services.yaml have a domain_ownership entry
"""

import yaml
from pathlib import Path

from sda.validators import CheckResult, Severity
from sda.discovery import load_all_services

REQUIRED_KEYS = {"roles", "triage_policy"}


def validate_owners(owners_file: Path) -> list[CheckResult]:
    """Validate OWNERS.yaml structure."""
    results: list[CheckResult] = []

    if not owners_file.exists():
        results.append(CheckResult(Severity.ERROR, f"OWNERS.yaml not found at {owners_file}"))
        return results

    with owners_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    for key in REQUIRED_KEYS:
        if key not in data:
            results.append(CheckResult(Severity.ERROR, f"OWNERS.yaml missing required key: '{key}'", owners_file))

    roles = data.get("roles", {}) or {}
    if "architecture_lead" not in roles:
        results.append(CheckResult(Severity.ERROR, "OWNERS.yaml missing 'roles.architecture_lead'", owners_file))
    else:
        lead = roles["architecture_lead"] or {}
        if not lead.get("name") or lead["name"].startswith("["):
            results.append(CheckResult(Severity.WARNING, "architecture_lead name is still a placeholder", owners_file))
        if not lead.get("email") or lead.get("email", "").startswith("["):
            results.append(CheckResult(Severity.WARNING, "architecture_lead email is still a placeholder", owners_file))

    return results


def validate_domain_coverage(owners_file: Path, services_file: Path, *, model_dir: Path | None = None) -> list[CheckResult]:
    """Ensure all services have a domain_ownership entry in OWNERS.yaml."""
    results: list[CheckResult] = []

    if not owners_file.exists():
        return results

    with owners_file.open(encoding="utf-8") as f:
        owners_data = yaml.safe_load(f) or {}

    domain_ownership = owners_data.get("domain_ownership") or {}

    # Collect service names from all sources
    service_names: set[str] = set()

    if model_dir is not None and model_dir.exists():
        all_services, _groups, _errors = load_all_services(model_dir)
        service_names.update(all_services.keys())
    elif services_file.exists():
        with services_file.open(encoding="utf-8") as f:
            services_data = yaml.safe_load(f) or {}
        service_names.update((services_data.get("services") or {}).keys())

    for name in sorted(service_names):
        if name not in domain_ownership:
            results.append(CheckResult(
                Severity.WARNING,
                f"Service '{name}' has no domain_ownership entry in OWNERS.yaml",
                owners_file,
            ))

    return results


def get_triage_sla(owners_file: Path) -> int:
    """Return inbox_sla_hours from OWNERS.yaml, defaulting to 48."""
    if not owners_file.exists():
        return 48
    with owners_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return (data.get("triage_policy") or {}).get("inbox_sla_hours", 48)
