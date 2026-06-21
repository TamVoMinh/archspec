"""
sda index — generate or validate the knowledge graph index.

Usage:
  sda index             # generate architecture/index.yaml
  sda index --validate  # check if committed index is up to date (non-blocking)
"""

import re
import yaml
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.table import Table

from sda.discovery import ARCH_DIR, INBOX_DIR, discover_partitions, discover_problem_files, load_all_services, load_partition_labels

ADR_DIR = Path("architecture/adr")
MODEL_DIR = Path("architecture/model")
INDEX_FILE = Path("architecture/index.yaml")
TEMPLATE_FILE = "TEMPLATE.md"

_META_RE = re.compile(r"##\s+Metadata\s*\n((?:\s*-\s+[\w_]+:.*\n?)*)", re.MULTILINE)
_FIELD_RE = re.compile(r"-\s+([\w_]+):\s*(.*)")
_SERVICES_RE = re.compile(r"##\s+Affected Services\s*\n((?:\s*-\s+.*\n?)*)", re.MULTILINE)


def _parse_meta_fields(content: str) -> dict:
    match = _META_RE.search(content)
    if not match:
        return {}
    fields: dict = {}
    for line in match.group(1).splitlines():
        m = _FIELD_RE.match(line.strip())
        if m:
            k, v = m.group(1), m.group(2).strip()
            if v in ("~", "", "null"):
                fields[k] = None
            elif v.startswith("[") and v.endswith("]"):
                inner = v[1:-1].strip()
                fields[k] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
            else:
                fields[k] = v
    return fields


def _affected_services(content: str) -> list[str]:
    m = _SERVICES_RE.search(content)
    if not m:
        return []
    return [l.strip().lstrip("- ").strip() for l in m.group(1).splitlines() if l.strip().lstrip("- ").strip()]


def _build_graph(
    project_dir: Path,
    *,
    adr_dir: Path | None = None,
    model_dir: Path | None = None,
    problem_files: list[Path] | None = None,
) -> dict:
    """Build a knowledge graph from problems, ADRs, and services.

    When called with defaults (no kwargs), scans the standard flat paths.
    When called with explicit paths, builds a scoped graph (for partitions).
    """
    from collections import defaultdict

    inbox = project_dir / INBOX_DIR
    _adr_dir = adr_dir if adr_dir is not None else project_dir / ADR_DIR
    _model_dir = model_dir if model_dir is not None else project_dir / MODEL_DIR
    graph: dict = {}
    service_index: dict = defaultdict(lambda: {"problems": [], "adrs": []})

    # Problems — use provided list or discover from inbox
    prob_files = problem_files if problem_files is not None else discover_problem_files(inbox)
    for f in prob_files:
        with f.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        prob_id = data.get("id") or f.stem.upper()
        services = data.get("services") or []
        graph[prob_id] = {
            "type": "problem",
            "services": services,
            "status": data.get("status", "active"),
            "linked_adrs": [],
        }
        if data.get("labels"):
            graph[prob_id]["labels"] = data["labels"]
        for svc in services:
            if prob_id not in service_index[svc]["problems"]:
                service_index[svc]["problems"].append(prob_id)

    # ADRs
    if _adr_dir.exists():
        for f in sorted(_adr_dir.glob("*.md")):
            if f.name == TEMPLATE_FILE:
                continue
            content = f.read_text(encoding="utf-8")
            meta = _parse_meta_fields(content)
            if not meta:
                continue
            adr_id = f.stem.upper()
            links = meta.get("links") or []
            if isinstance(links, str):
                links = [links]
            prob_links = [l for l in links if l.startswith("PROB-")]
            adr_services = _affected_services(content)
            graph[adr_id] = {
                "type": "adr",
                "status": meta.get("status", "proposed"),
                "linked_problems": prob_links,
                "linked_services": adr_services,
                "superseded_by": meta.get("superseded_by"),
            }
            raw_labels = meta.get("labels")
            if isinstance(raw_labels, str):
                from sda.validators.adr import parse_label_string
                adr_labels = parse_label_string(raw_labels)
                if adr_labels:
                    graph[adr_id]["labels"] = adr_labels
            for prob_id in prob_links:
                if prob_id in graph and adr_id not in graph[prob_id]["linked_adrs"]:
                    graph[prob_id]["linked_adrs"].append(adr_id)
            for svc in adr_services:
                if adr_id not in service_index[svc]["adrs"]:
                    service_index[svc]["adrs"].append(adr_id)

    # Service nodes — from references + hierarchical model
    all_services, groups, _svc_errors = load_all_services(_model_dir)

    # Add referenced services (from problems/ADRs)
    for svc_name, svc_data in service_index.items():
        node: dict = {
            "type": "service",
            "problems": svc_data["problems"],
            "adrs": svc_data["adrs"],
            "depends_on": [],
        }
        if svc_name in all_services:
            meta = all_services[svc_name]
            group = meta.get("_group")
            if group is not None:
                node["group"] = group
            node["depends_on"] = list(meta.get("depends_on") or [])
            if meta.get("labels"):
                node["labels"] = meta["labels"]
        graph[svc_name] = node

    # Add model-defined services not yet referenced
    for svc_name, meta in all_services.items():
        if svc_name not in graph:
            node: dict = {
                "type": "service",
                "problems": [],
                "adrs": [],
                "depends_on": list(meta.get("depends_on") or []),
            }
            group = meta.get("_group")
            if group is not None:
                node["group"] = group
            if meta.get("labels"):
                node["labels"] = meta["labels"]
            graph[svc_name] = node

    # Add group nodes
    for group_name, children in groups.items():
        graph[group_name] = {
            "type": "group",
            "children": sorted(children),
        }

    return graph


def _render(graph: dict, *, systems: list[str] | None = None) -> str:
    header = "# AUTO-GENERATED by `sda index` — do not edit manually\n"
    data: dict = {}
    if systems:
        data["systems"] = systems
    data["graph"] = graph
    return header + yaml.dump(data, default_flow_style=False, sort_keys=True, allow_unicode=True)


def _render_manifest(
    systems: list[str],
    partitions: list[tuple[str, Path]],
    master_graph: dict,
    arch_dir: Path,
    *,
    unscoped_graph: dict,
) -> str:
    """Render a slim manifest that points to per-system index files."""
    header = "# AUTO-GENERATED by `sda index` — do not edit manually\n"
    header += "# Full graphs live in each partition's index.yaml\n"

    data: dict = {"systems": systems, "partitions": {}}

    for part_name, part_path in partitions:
        rel = part_path.relative_to(arch_dir)
        n_p = sum(1 for v in master_graph.values() if v.get("type") == "problem" and v.get("system") == part_name)
        n_a = sum(1 for v in master_graph.values() if v.get("type") == "adr" and v.get("system") == part_name)
        n_s = sum(1 for v in master_graph.values() if v.get("type") == "service" and v.get("system") == part_name)
        data["partitions"][part_name] = {
            "index": f"{rel}/index.yaml",
            "problems": n_p,
            "adrs": n_a,
            "services": n_s,
        }
        part_labels = load_partition_labels(part_path)
        if part_labels:
            data["partitions"][part_name]["labels"] = part_labels

    # Unscoped nodes (root ADRs, unrouted problems) — inline since they're small
    unscoped_nodes = {
        k: v for k, v in unscoped_graph.items() if "system" not in v
    }
    if unscoped_nodes:
        data["unscoped"] = unscoped_nodes

    return header + yaml.dump(data, default_flow_style=False, sort_keys=True, allow_unicode=True)


def _route_problems(inbox: Path, partition_names: set[str]) -> tuple[dict[str, list[Path]], list[Path]]:
    """Route problems to partitions by system: field.

    Returns:
        - routed: dict of partition_name -> list of problem file paths
        - unrouted: list of problem file paths with no/unmatched system
    """
    routed: dict[str, list[Path]] = {name: [] for name in partition_names}
    unrouted: list[Path] = []

    for f in discover_problem_files(inbox):
        with f.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        system = data.get("system")
        if system and system in partition_names:
            routed[system].append(f)
        else:
            unrouted.append(f)

    return routed, unrouted


def _annotate_graph(graph: dict, system: str) -> dict:
    """Add system: field to every node in a graph."""
    annotated = {}
    for key, node in graph.items():
        annotated[key] = {**node, "system": system}
    return annotated


def _merge_into(target: dict, source: dict) -> None:
    """Deep-merge source graph nodes into target, combining list fields for services."""
    for key, node in source.items():
        if key in target and target[key].get("type") == "service" and node.get("type") == "service":
            existing = target[key]
            for field in ("problems", "adrs", "depends_on"):
                merged = list(existing.get(field, []))
                for item in node.get(field, []):
                    if item not in merged:
                        merged.append(item)
                existing[field] = merged
            # Preserve system annotation if already set
            if "system" not in existing and "system" in node:
                existing["system"] = node["system"]
        else:
            target[key] = node


def _build_partitioned_graphs(
    project_dir: Path,
    partitions: list[tuple[str, Path]],
) -> tuple[dict, list[tuple[str, Path, dict]]]:
    """Build the master graph plus each partition's scoped graph (no file writes).

    Returns:
        - master_graph: merged, system-annotated graph including root ADRs and unrouted problems
        - part_graphs: list of (partition_name, partition_path, partition_graph)
    """
    partition_names = {name for name, _ in partitions}
    inbox = project_dir / INBOX_DIR
    routed, unrouted = _route_problems(inbox, partition_names)

    master_graph: dict = {}
    part_graphs: list[tuple[str, Path, dict]] = []

    for part_name, part_path in partitions:
        part_graph = _build_graph(
            project_dir,
            adr_dir=part_path / "adr",
            model_dir=part_path / "model",
            problem_files=routed.get(part_name, []),
        )
        part_graphs.append((part_name, part_path, part_graph))
        # Merge into master with system annotations
        _merge_into(master_graph, _annotate_graph(part_graph, part_name))

    # Add root-level ADRs to master only
    root_adr_dir = project_dir / ADR_DIR
    if root_adr_dir.exists():
        root_adr_graph = _build_graph(
            project_dir,
            adr_dir=root_adr_dir,
            model_dir=root_adr_dir / "_no_model",  # no services from root
            problem_files=[],
        )
        _merge_into(master_graph, root_adr_graph)

    # Add unrouted problems to master only
    if unrouted:
        unrouted_graph = _build_graph(
            project_dir,
            adr_dir=inbox / "_no_adr",  # no ADRs
            model_dir=inbox / "_no_model",  # no services
            problem_files=unrouted,
        )
        _merge_into(master_graph, unrouted_graph)

    return master_graph, part_graphs


def assemble_graph(project_dir: Path) -> tuple[dict, list[tuple[str, Path]]]:
    """Build the full knowledge graph for a project without writing any files.

    Returns (graph, partitions). In flat mode `graph` is the flat graph and
    `partitions` is empty; in partitioned mode `graph` is the merged, system-annotated
    master graph. Shared by `sda index`, `sda graph`, and `sda build`.
    """
    partitions = discover_partitions(project_dir / ARCH_DIR)
    if not partitions:
        return _build_graph(project_dir), partitions
    master_graph, _ = _build_partitioned_graphs(project_dir, partitions)
    return master_graph, partitions


def index(
    validate: Annotated[bool, typer.Option("--validate", help="Validate committed index is up to date (non-blocking)")] = False,
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Generate or validate the architecture/index.yaml knowledge graph."""
    arch_dir = project_dir / ARCH_DIR
    partitions = discover_partitions(arch_dir)
    index_file = project_dir / INDEX_FILE

    if not partitions:
        # ── Flat mode (backward compatible) ──
        graph = _build_graph(project_dir)
        output = _render(graph)

        if validate:
            _validate_index(index_file, output)

        index_file.parent.mkdir(parents=True, exist_ok=True)
        index_file.write_text(output, encoding="utf-8")

        _print_summary(graph, index_file)
    else:
        # ── Partitioned mode ──
        partition_names = {name for name, _ in partitions}
        master_graph, part_graphs = _build_partitioned_graphs(project_dir, partitions)

        # Write per-partition indexes
        for _part_name, part_path, part_graph in part_graphs:
            (part_path / "index.yaml").write_text(_render(part_graph), encoding="utf-8")

        # Write master index as slim manifest
        systems_list = sorted(partition_names)
        master_manifest = _render_manifest(
            systems_list, partitions, master_graph, arch_dir, unscoped_graph=master_graph,
        )

        if validate:
            _validate_index(index_file, master_manifest)

        index_file.parent.mkdir(parents=True, exist_ok=True)
        index_file.write_text(master_manifest, encoding="utf-8")

        _print_partitioned_summary(master_graph, partitions, index_file)


def _validate_index(index_file: Path, expected_output: str) -> None:
    if not index_file.exists():
        rprint("[yellow]WARNING:[/yellow] architecture/index.yaml not found — run [bold]sda index[/bold] to generate")
        raise typer.Exit(0)
    committed = index_file.read_text(encoding="utf-8")
    if committed != expected_output:
        rprint("[yellow]WARNING:[/yellow] architecture/index.yaml is stale — run [bold]sda index[/bold] to regenerate")
    else:
        rprint("[green]✓[/green] knowledge graph index is up to date")
    raise typer.Exit(0)


def _print_summary(graph: dict, index_file: Path) -> None:
    from rich.console import Console

    n_problems = sum(1 for v in graph.values() if v.get("type") == "problem")
    n_adrs = sum(1 for v in graph.values() if v.get("type") == "adr")
    n_services = sum(1 for v in graph.values() if v.get("type") == "service")
    n_groups = sum(1 for v in graph.values() if v.get("type") == "group")

    table = Table(title="Knowledge Graph", show_header=True, header_style="bold cyan")
    table.add_column("Type")
    table.add_column("Count", justify="right")
    table.add_row("Problems", str(n_problems))
    table.add_row("ADRs", str(n_adrs))
    table.add_row("Services", str(n_services))
    if n_groups:
        table.add_row("Groups", str(n_groups))

    Console().print(table)
    rprint(f"\n[green]✓[/green] Written to {index_file}")


def _print_partitioned_summary(graph: dict, partitions: list[tuple[str, Path]], index_file: Path) -> None:
    from rich.console import Console

    table = Table(title="Knowledge Graph (partitioned)", show_header=True, header_style="bold cyan")
    table.add_column("Partition")
    table.add_column("Problems", justify="right")
    table.add_column("ADRs", justify="right")
    table.add_column("Services", justify="right")

    for part_name, _ in partitions:
        n_p = sum(1 for v in graph.values() if v.get("type") == "problem" and v.get("system") == part_name)
        n_a = sum(1 for v in graph.values() if v.get("type") == "adr" and v.get("system") == part_name)
        n_s = sum(1 for v in graph.values() if v.get("type") == "service" and v.get("system") == part_name)
        table.add_row(part_name, str(n_p), str(n_a), str(n_s))

    # Unscoped (root ADRs + unrouted problems)
    n_unscoped_p = sum(1 for v in graph.values() if v.get("type") == "problem" and "system" not in v)
    n_unscoped_a = sum(1 for v in graph.values() if v.get("type") == "adr" and "system" not in v)
    if n_unscoped_p or n_unscoped_a:
        table.add_row("[dim](unscoped)[/dim]", str(n_unscoped_p), str(n_unscoped_a), "0")

    Console().print(table)
    rprint(f"\n[green]✓[/green] Written to {index_file} + {len(partitions)} partition index(es)")
