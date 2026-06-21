"""
ADR lifecycle validators.

Checks:
- Every ADR has a ## Metadata block with status and date
- Status value is in the allowed set
- superseded ADRs have a non-null superseded_by
- All required sections are present
"""

import re
from pathlib import Path

from sda.validators import CheckResult, Severity

VALID_STATUSES = {"proposed", "accepted", "rejected", "superseded", "deprecated"}
REQUIRED_SECTIONS = {"## Context", "## Decision", "## Alternatives", "## Consequences", "## Affected Services"}
TEMPLATE_FILENAME = "TEMPLATE.md"

_METADATA_RE = re.compile(
    r"##\s+Metadata\s*\n((?:\s*-\s+[\w_]+:.*\n?)*)",
    re.MULTILINE,
)
_FIELD_RE = re.compile(r"-\s+([\w_]+):\s*(.*)")


def _parse_metadata(content: str) -> dict:
    match = _METADATA_RE.search(content)
    if not match:
        return {}
    fields: dict = {}
    for line in match.group(1).splitlines():
        m = _FIELD_RE.match(line.strip())
        if m:
            key, value = m.group(1), m.group(2).strip()
            if value in ("~", "", "null"):
                fields[key] = None
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                fields[key] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
            else:
                fields[key] = value
    return fields


def _check_adr_file(path: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    content = path.read_text(encoding="utf-8")
    meta = _parse_metadata(content)

    if not meta:
        results.append(CheckResult(Severity.ERROR, "Missing ## Metadata block", path))
        return results

    # Required: status
    if "status" not in meta:
        results.append(CheckResult(Severity.ERROR, "Missing 'status' field in ## Metadata", path))
    else:
        status = meta["status"]
        if status not in VALID_STATUSES:
            results.append(CheckResult(
                Severity.ERROR,
                f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
                path,
            ))
        elif status == "superseded" and not meta.get("superseded_by"):
            results.append(CheckResult(
                Severity.ERROR,
                "status is 'superseded' but 'superseded_by' is null or missing",
                path,
            ))

    # Required: date
    if "date" not in meta:
        results.append(CheckResult(Severity.WARNING, "Missing 'date' field in ## Metadata", path))

    # Required sections
    for section in REQUIRED_SECTIONS:
        if section not in content:
            results.append(CheckResult(Severity.WARNING, f"Missing section '{section}'", path))

    return results


def validate_adrs(adr_dir: Path) -> list[CheckResult]:
    """Validate all ADR files in adr_dir."""
    if not adr_dir.exists():
        return []

    results: list[CheckResult] = []
    adr_files = [f for f in sorted(adr_dir.glob("*.md")) if f.name != TEMPLATE_FILENAME]

    if not adr_files:
        return []

    for adr_path in adr_files:
        results.extend(_check_adr_file(adr_path))

    return results


def get_adr_status(content: str) -> str | None:
    meta = _parse_metadata(content)
    return meta.get("status")


def parse_label_string(raw: str) -> dict:
    """Parse an ADR metadata `labels` line: `area=payments, criticality=core`."""
    out: dict = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if "=" in pair:
            k, v = pair.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def get_labels(content: str) -> dict:
    """Classification labels declared in an ADR's ## Metadata block."""
    raw = _parse_metadata(content).get("labels")
    return parse_label_string(raw) if isinstance(raw, str) else {}


def get_affected_services(content: str) -> list[str]:
    match = re.search(r"##\s+Affected Services\s*\n((?:\s*-\s+.*\n?)*)", content, re.MULTILINE)
    if not match:
        return []
    return [line.strip().lstrip("- ").strip() for line in match.group(1).splitlines() if line.strip().lstrip("- ").strip()]


def validate_adr_service_refs(adr_dir: Path, services_file: Path) -> list[CheckResult]:
    """Ensure no accepted ADR references a deprecated service."""
    import yaml

    results: list[CheckResult] = []

    deprecated: set[str] = set()
    if services_file.exists():
        with services_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        deprecated = {
            name for name, meta in (data.get("services") or {}).items()
            if (meta or {}).get("deprecated")
        }

    if not adr_dir.exists() or not deprecated:
        return results

    for adr_path in sorted(adr_dir.glob("*.md")):
        if adr_path.name == TEMPLATE_FILENAME:
            continue
        content = adr_path.read_text(encoding="utf-8")
        if get_adr_status(content) != "accepted":
            continue
        for svc in get_affected_services(content):
            if svc in deprecated:
                results.append(CheckResult(
                    Severity.ERROR,
                    f"Accepted ADR references deprecated service '{svc}'",
                    adr_path,
                ))

    return results


def validate_adr_service_existence(
    adr_dir: Path,
    services_file: Path,
    *,
    model_dir: Path | None = None,
) -> list[CheckResult]:
    """Warn when an ADR's ## Affected Services lists a service not in the registry."""
    from sda.validators.services import load_service_names

    results: list[CheckResult] = []
    if not adr_dir.exists():
        return results

    known = load_service_names(services_file, model_dir=model_dir)

    for adr_path in sorted(adr_dir.glob("*.md")):
        if adr_path.name == TEMPLATE_FILENAME:
            continue
        content = adr_path.read_text(encoding="utf-8")
        for svc in get_affected_services(content):
            if svc not in known:
                results.append(CheckResult(
                    Severity.WARNING,
                    f"ADR references unknown service '{svc}' in ## Affected Services",
                    adr_path,
                ))

    return results
