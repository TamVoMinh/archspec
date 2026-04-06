"""
aos status — show a health overview of the current SDA project.

Usage:
  aos status
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

ADR_DIR = Path("architecture/adr")
INBOX_DIR = Path("architecture/inbox")
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


def status(
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Show health overview: problems, ADRs, services, index freshness."""
    pd = project_dir
    console = Console()

    # --- Problems ---
    inbox = pd / INBOX_DIR
    problems = {"draft": 0, "active": 0, "resolved": 0, "total": 0}
    if inbox.exists():
        for f in inbox.glob("PROB-[0-9]*.yaml"):
            with f.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            s = data.get("status", "active")
            problems[s] = problems.get(s, 0) + 1
            problems["total"] += 1

    # --- ADRs ---
    adr_dir = pd / ADR_DIR
    adrs: dict[str, int] = {"total": 0}
    if adr_dir.exists():
        for f in adr_dir.glob("*.md"):
            if f.name == TEMPLATE_FILE:
                continue
            s = _get_status(f.read_text(encoding="utf-8"))
            adrs[s] = adrs.get(s, 0) + 1
            adrs["total"] += 1

    # --- Services ---
    svcs_file = pd / SERVICES_FILE
    stale_count = 0
    svc_total = 0
    if svcs_file.exists():
        with svcs_file.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        today = date.today()
        for _, meta in (data.get("services") or {}).items():
            svc_total += 1
            lr = (meta or {}).get("last_reviewed")
            if lr:
                try:
                    age = (today - date.fromisoformat(str(lr))).days
                    if age > 180:
                        stale_count += 1
                except ValueError:
                    pass

    # --- Index freshness ---
    index_file = pd / INDEX_FILE
    index_status = "[dim]not generated[/dim]"
    if index_file.exists():
        mtime = date.fromtimestamp(index_file.stat().st_mtime)
        age = (date.today() - mtime).days
        if age == 0:
            index_status = "[green]fresh (today)[/green]"
        elif age <= 7:
            index_status = f"[yellow]{age}d old[/yellow]"
        else:
            index_status = f"[red]{age}d old — run [bold]sda index[/bold][/red]"

    # --- Render ---
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
    table.add_row(
        "Services",
        f"{svc_total} total" + (f"  [yellow]{stale_count} stale[/yellow]" if stale_count else "  [green]none stale[/green]"),
    )
    table.add_row("Index", index_status)

    console.print(Panel(table, title="[bold]ArchSpec Status[/bold]", border_style="cyan"))
