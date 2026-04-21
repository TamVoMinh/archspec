"""
Shared discovery utilities for scanning inbox problems and service models.

Both flat (PROB-XXX.yaml) and folder (PROB-XXX/PROB-XXX.yaml) layouts are supported.
Service models support recursive discovery across subdirectories.
Multi-partition architecture hubs are auto-discovered by structure.
"""

import re
import yaml
from pathlib import Path


ARCH_DIR = Path("architecture")
INBOX_DIR = Path("architecture/inbox")
MODEL_DIR = Path("architecture/model")
SERVICES_FILENAME = "services.yaml"
TEMPLATE_FILENAME = "PROB-TEMPLATE.yaml"

_PROB_ID_RE = re.compile(r"PROB-(\d+)", re.IGNORECASE)

_RESERVED_DIRS = frozenset({"inbox", "model", "adr"})


def discover_partitions(arch_dir: Path) -> list[tuple[str, Path]]:
    """Discover partitions inside the architecture directory.

    A direct child directory is a partition if it contains model/ or adr/ (or both).
    Reserved directory names (inbox, model, adr) are never treated as partitions.

    Returns a sorted list of (name, path) tuples.
    """
    if not arch_dir.exists():
        return []

    partitions: list[tuple[str, Path]] = []
    for child in sorted(arch_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name in _RESERVED_DIRS:
            continue
        has_model = (child / "model").is_dir()
        has_adr = (child / "adr").is_dir()
        if has_model or has_adr:
            partitions.append((child.name, child))

    return partitions


def discover_problem_files(inbox: Path) -> list[Path]:
    """Discover all PROB-*.yaml files in both flat and folder layouts.

    Returns a sorted, deduplicated list of paths.
    Raises ValueError if a problem ID appears in both layouts.
    """
    if not inbox.exists():
        return []

    flat: dict[str, Path] = {}
    folder: dict[str, Path] = {}

    # Flat: architecture/inbox/PROB-001.yaml
    for f in inbox.glob("PROB-[0-9]*.yaml"):
        if f.name == TEMPLATE_FILENAME:
            continue
        m = _PROB_ID_RE.match(f.stem)
        if m:
            flat[f.stem.upper()] = f

    # Folder: architecture/inbox/PROB-001/PROB-001.yaml
    for f in inbox.glob("PROB-[0-9]*/PROB-[0-9]*.yaml"):
        if f.name == TEMPLATE_FILENAME:
            continue
        m = _PROB_ID_RE.match(f.stem)
        if m:
            folder[f.stem.upper()] = f

    # Check for duplicates across layouts
    duplicates = set(flat.keys()) & set(folder.keys())
    if duplicates:
        raise ValueError(
            f"Duplicate problem ID(s) found in both flat and folder layouts: {', '.join(sorted(duplicates))}"
        )

    merged = {**flat, **folder}
    return sorted(merged.values(), key=lambda p: p.name)


def discover_max_prob_id(inbox: Path) -> int:
    """Find the highest PROB-NNN integer across both flat and folder layouts."""
    if not inbox.exists():
        return 0

    ids: list[int] = []

    # Flat files
    for f in inbox.glob("PROB-[0-9]*.yaml"):
        m = re.match(r"PROB-(\d+)\.yaml", f.name, re.IGNORECASE)
        if m:
            ids.append(int(m.group(1)))

    # Folders
    for d in inbox.iterdir():
        if d.is_dir():
            m = re.match(r"PROB-(\d+)", d.name, re.IGNORECASE)
            if m:
                ids.append(int(m.group(1)))

    return max(ids, default=0)


def discover_service_files(model_dir: Path) -> list[tuple[str | None, Path]]:
    """Recursively discover all services.yaml files under the model directory.

    Returns a list of (group_name, path) tuples.
    Root-level services.yaml has group_name=None.
    Subdirectory services.yaml has group_name=subdirectory name.
    """
    if not model_dir.is_dir():
        return []

    results: list[tuple[str | None, Path]] = []

    # Root level
    root_file = model_dir / SERVICES_FILENAME
    if root_file.exists():
        results.append((None, root_file))

    # Subdirectories (one level deep)
    for child in sorted(model_dir.iterdir()):
        if child.is_dir():
            sub_file = child / SERVICES_FILENAME
            if sub_file.exists():
                results.append((child.name, sub_file))

    return results


def load_all_services(model_dir: Path) -> tuple[dict[str, dict], dict[str, list[str]], list[str]]:
    """Load all services from all discovered services.yaml files.

    Returns:
        - all_services: merged dict of service_name -> meta (with 'group' added)
        - groups: dict of group_name -> list of service names
        - errors: list of error messages (e.g., duplicate service names)
    """
    service_files = discover_service_files(model_dir)
    all_services: dict[str, dict] = {}
    groups: dict[str, list[str]] = {}
    errors: list[str] = []

    for group_name, path in service_files:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        for name, meta in (data.get("services") or {}).items():
            if name in all_services:
                existing_group = all_services[name].get("_group")
                errors.append(
                    f"Duplicate service '{name}' found in "
                    f"{'root' if existing_group is None else existing_group} and "
                    f"{'root' if group_name is None else group_name}"
                )
                continue

            meta = meta or {}
            meta["_group"] = group_name
            meta["_file"] = path
            all_services[name] = meta

            if group_name is not None:
                groups.setdefault(group_name, []).append(name)

    return all_services, groups, errors
