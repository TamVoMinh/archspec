"""
sda status — show a health overview of the current SDA project.

Usage:
  sda status
"""

import yaml
import re
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from sda.discovery import ARCH_DIR, INBOX_DIR, discover_partitions, discover_problem_files, load_all_services

ADR_DIR = Path("architecture/adr")
MODEL_DIR = Path("architecture/model")
SERVICES_FILE = Path("architecture/model/services.yaml")
INDEX_FILE = Path("architecture/index.yaml")
OWNERS_FILE = Path("OWNERS.yaml")
TEMPLATE_FILE = "TEMPLATE.md"

_META_RE = re.compile(r"##\s+Metadata\s*\n((?:\s*-\s+[\w_]+:.*\n?)*)", re.MULTILINE)
_FIELD_RE = re.compile(r"-\s+([\w_]+):\s*(.*)")


def _get_status(content: str) -> str:
    m = _META_RE.search(content)
    if not m:
        return "unknown"
    for line in m.group(1).splitlines():
        fm = _FIELD_RE.match(line.strip())
        if fm and fm.group(1) == "status":
            return fm.group(2).strip()
    return "unknown"


def _count_adrs(adr_dir: Path) -> dict[str, int]:
    adrs: dict[str, int] = {"total": 0}
    if not adr_dir.exists():
        return adrs
    for f in adr_dir.glob("*.md"):
        if f.name == TEMPLATE_FILE:
            continue
        s = _get_status(f.read_text(encoding="utf-8"))
        adrs[s] = adrs.get(s, 0) + 1
        adrs["total"] += 1
    return adrs


def _count_services(model_dir: Path) -> tuple[int, int, dict[str, int], int]:
    """Return (total, stale_count, group_counts, root_count)."""
    stale_count = 0
    svc_total = 0
    group_counts: dict[str, int] = {}
    root_count = 0

    if not model_dir.exists():
        return svc_total, stale_count, group_counts, root_count

    all_services, groups, _errors = load_all_services(model_dir)
    today = date.today()
    for name, meta in all_services.items():
        svc_total += 1
        group = meta.get("_group")
        if group is not None:
            group_counts[group] = group_counts.get(group, 0) + 1
        else:
            root_count += 1
        lr = meta.get("last_reviewed")
        if lr:
            try:
                age = (today - date.fromisoformat(str(lr))).days
                if age > 180:
                    stale_count += 1
            except ValueError:
                pass

    return svc_total, stale_count, group_counts, root_count


def _index_freshness(index_file: Path) -> str:
    if not index_file.exists():
        return "[dim]not generated[/dim]"
    mtime = date.fromtimestamp(index_file.stat().st_mtime)
    age = (date.today() - mtime).days
    if age == 0:
        return "[green]fresh (today)[/green]"
    elif age <= 7:
        return f"[yellow]{age}d old[/yellow]"
    return f"[red]{age}d old — run [bold]sda index[/bold][/red]"


def status(
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Show health overview: problems, ADRs, services, index freshness."""
    pd = project_dir
    console = Console()
    arch_dir = pd / ARCH_DIR
    partitions = discover_partitions(arch_dir)

    if partitions:
        _status_partitioned(pd, console, partitions)
    else:
        _status_flat(pd, console)


def _status_flat(pd: Path, console: Console) -> None:
    """Flat-mode status display."""
    inbox = pd / INBOX_DIR
    problems = {"draft": 0, "active": 0, "resolved": 0, "total": 0}
    if inbox.exists():
        for f in discover_problem_files(inbox):
            with f.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            s = data.get("status", "active")
            problems[s] = problems.get(s, 0) + 1
            problems["total"] += 1

    adrs = _count_adrs(pd / ADR_DIR)
    svc_total, stale_count, group_counts, root_count = _count_services(pd / MODEL_DIR)

    # If no model dir, try single file fallback
    if svc_total == 0 and (pd / SERVICES_FILE).exists():
        svcs_file = pd / SERVICES_FILE
        with svcs_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        today = date.today()
        for _, meta in (data.get("services") or {}).items():
            svc_total += 1
            root_count += 1
            lr = (meta or {}).get("last_reviewed")
            if lr:
                try:
                    age = (today - date.fromisoformat(str(lr))).days
                    if age > 180:
                        stale_count += 1
                except ValueError:
                    pass

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Category", style="bold")
    table.add_column("Details")

    table.add_row(
        "Problems",
        f"{problems['total']} total  "
        f"[cyan]{problems.get('active', 0)} active[/cyan]  "
        f"[dim]{problems.get('draft', 0)} draft[/dim]  "
        f"[green]{problems.get('resolved', 0)} resolved[/green]",
    )
    table.add_row(
        "ADRs",
        f"{adrs.get('total', 0)} total  "
        f"[green]{adrs.get('accepted', 0)} accepted[/green]  "
        f"[cyan]{adrs.get('proposed', 0)} proposed[/cyan]  "
        f"[dim]{adrs.get('superseded', 0)} superseded[/dim]",
    )
    svc_detail = f"{svc_total} total"
    if group_counts:
        parts = [f"{root_count} root" if root_count else None]
        parts.extend(f"{count} in {gname}" for gname, count in sorted(group_counts.items()))
        svc_detail += f" ({', '.join(p for p in parts if p)})"
    svc_detail += f"  [yellow]{stale_count} stale[/yellow]" if stale_count else "  [green]none stale[/green]"

    table.add_row("Services", svc_detail)
    table.add_row("Index", _index_freshness(pd / INDEX_FILE))

    console.print(Panel(table, title="[bold]ArchSpec Status[/bold]", border_style="cyan"))


def _status_partitioned(pd: Path, console: Console, partitions: list[tuple[str, Path]]) -> None:
    """Partitioned-mode status display."""
    inbox = pd / INBOX_DIR
    partition_names = {name for name, _ in partitions}

    # Count problems and route by system
    problems_by_system: dict[str, dict[str, int]] = {}
    unrouted_count = 0
    total_problems = 0

    if inbox.exists():
        for f in discover_problem_files(inbox):
            with f.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            total_problems += 1
            system = data.get("system")
            if system and system in partition_names:
                bucket = problems_by_system.setdefault(system, {"total": 0})
                bucket["total"] += 1
                s = data.get("status", "active")
                bucket[s] = bucket.get(s, 0) + 1
            else:
                unrouted_count += 1

    # Per-partition table
    table = Table(title="ArchSpec Status (partitioned)", show_header=True)
    table.add_column("Partition")
    table.add_column("Problems", justify="right")
    table.add_column("ADRs", justify="right")
    table.add_column("Services", justify="right")

    for name, part_path in partitions:
        p_count = problems_by_system.get(name, {}).get("total", 0)
        a_count = _count_adrs(part_path / "adr").get("total", 0)
        s_total, _, _, _ = _count_services(part_path / "model")
        table.add_row(name, str(p_count), str(a_count), str(s_total))

    # Root ADRs
    root_adr_count = _count_adrs(pd / ADR_DIR).get("total", 0)
    if root_adr_count or unrouted_count:
        table.add_row("(root)", str(unrouted_count), str(root_adr_count), "—")

    console.print(table)

    # Summary line
    rprint(
        f"\n[bold]Systems:[/bold] {len(partitions)} ({', '.join(n for n, _ in partitions)})"
        f"  [bold]Total problems:[/bold] {total_problems}"
        + (f"  [yellow]{unrouted_count} unrouted[/yellow]" if unrouted_count else "")
    )
    rprint(f"[bold]Index:[/bold] {_index_freshness(pd / INDEX_FILE)}")
