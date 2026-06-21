"""
Classification dimensions — the methodology-neutral core for labeling artifacts.

The core ships dimension *names* with neutral defaults; `area` and `criticality` are
open (any value) until a project or a methodology pack closes them, while `lifecycle`
ships a neutral vocabulary. Projects override/extend via architecture/classification.yaml:

    dimensions:
      criticality:
        values: [core, supporting, generic]   # closed vocabulary (validated)
      team:
        values: ~                              # open dimension (any value)
"""

import yaml
from pathlib import Path

CLASSIFICATION_FILE = Path("architecture/classification.yaml")

# Default dimension names. `values: None` means open (any value accepted).
DEFAULT_DIMENSIONS: dict[str, dict] = {
    "area": {"values": None},
    "criticality": {"values": None},
    "lifecycle": {"values": ["active", "deprecated", "retired"]},
}


def load_dimensions(project_dir: Path) -> dict[str, dict]:
    """Return the active dimensions (defaults merged with architecture/classification.yaml)."""
    dims: dict[str, dict] = {name: dict(spec) for name, spec in DEFAULT_DIMENSIONS.items()}

    config = project_dir / CLASSIFICATION_FILE
    if config.exists():
        with config.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        for name, spec in (data.get("dimensions") or {}).items():
            spec = spec or {}
            dims[name] = {"values": spec.get("values")}  # None / missing → open

    return dims
