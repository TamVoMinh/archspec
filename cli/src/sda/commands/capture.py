"""
sda capture — scaffold a draft problem file.

Usage:
  sda capture "API latency spike"
  sda capture "Auth service memory leak" --source jira --type reliability
"""

import re
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.panel import Panel

INBOX_DIR = Path("architecture/inbox")
VALID_SOURCES = ("slack", "jira", "github", "meeting", "email", "adhoc")
VALID_TYPES = ("performance", "security", "reliability", "cost", "ux", "compliance", "other")


def _next_prob_id(inbox: Path) -> str:
    existing = []
    for f in inbox.glob("PROB-[0-9]*.yaml"):
        m = re.match(r"PROB-(\d+)\.yaml", f.name, re.IGNORECASE)
        if m:
            existing.append(int(m.group(1)))
    return f"PROB-{(max(existing, default=0) + 1):03d}"


def capture(
    title: Annotated[str, typer.Argument(help="Short description of the problem (5–200 chars)")],
    source: Annotated[str, typer.Option(help=f"Input source: {', '.join(VALID_SOURCES)}")] = "adhoc",
    type: Annotated[str, typer.Option(help=f"Problem type: {', '.join(VALID_TYPES)}")] = "other",
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Scaffold a new draft problem YAML file in architecture/inbox/."""
    if len(title) < 5:
        rprint("[red]Error:[/red] title must be at least 5 characters")
        raise typer.Exit(1)

    if source not in VALID_SOURCES:
        rprint(f"[red]Error:[/red] invalid source '{source}'. Choose from: {', '.join(VALID_SOURCES)}")
        raise typer.Exit(1)

    if type not in VALID_TYPES:
        rprint(f"[red]Error:[/red] invalid type '{type}'. Choose from: {', '.join(VALID_TYPES)}")
        raise typer.Exit(1)

    inbox = project_dir / INBOX_DIR
    inbox.mkdir(parents=True, exist_ok=True)

    prob_id = _next_prob_id(inbox)
    filename = inbox / f"{prob_id}.yaml"
    today = date.today().isoformat()

    content = f"""\
id: {prob_id}
title: "{title}"
source: {source}
type: {type}
created_at: {today}
status: draft

services: []    # Fill in during triage
symptoms: []    # Fill in during triage

constraints: []
tags: []
"""
    filename.write_text(content, encoding="utf-8")

    rprint(Panel(
        f"[green]Created:[/green] {filename}\n\n"
        f"[dim]Next:[/dim] fill in [bold]services[/bold] and [bold]symptoms[/bold], "
        f"then change status to [bold]active[/bold]",
        title=f"[bold]{prob_id}[/bold]",
        border_style="green",
    ))
