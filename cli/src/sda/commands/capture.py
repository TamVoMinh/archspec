"""
sda capture — scaffold a draft problem file.

Usage:
  sda capture "API latency spike"
  sda capture "Auth service memory leak" --source jira --type reliability
  sda capture "Ping test retirement" --source email --attach ~/notification.msg
"""

import shutil
from datetime import date
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print as rprint
from rich.panel import Panel

from sda.discovery import INBOX_DIR, discover_max_prob_id

VALID_SOURCES = ("slack", "jira", "github", "meeting", "email", "adhoc")
VALID_TYPES = ("performance", "security", "reliability", "cost", "ux", "compliance", "other")


def capture(
    title: Annotated[str, typer.Argument(help="Short description of the problem (5–200 chars)")],
    source: Annotated[str, typer.Option(help=f"Input source: {', '.join(VALID_SOURCES)}")] = "adhoc",
    type: Annotated[str, typer.Option(help=f"Problem type: {', '.join(VALID_TYPES)}")] = "other",
    system: Annotated[Optional[str], typer.Option(help="Target system/partition name")] = None,
    attach: Annotated[Optional[list[Path]], typer.Option("--attach", help="File(s) to attach alongside the problem")] = None,
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

    # Validate attachments exist before creating anything
    if attach:
        for att in attach:
            if not att.exists():
                rprint(f"[red]Error:[/red] attachment not found: {att}")
                raise typer.Exit(1)

    inbox = project_dir / INBOX_DIR
    inbox.mkdir(parents=True, exist_ok=True)

    next_num = discover_max_prob_id(inbox) + 1
    prob_id = f"PROB-{next_num:03d}"
    today = date.today().isoformat()

    content = f"""\
id: {prob_id}
title: "{title}"
source: {source}
type: {type}
created_at: {today}
status: draft
"""
    if system:
        content += f"system: {system}\n"

    content += """
services: []    # Fill in during triage
symptoms: []    # Fill in during triage

constraints: []
tags: []
"""
    # Decide layout: folder if attachments, flat otherwise
    use_folder = bool(attach)

    if use_folder:
        folder = inbox / prob_id
        folder.mkdir(parents=True, exist_ok=True)
        filename = folder / f"{prob_id}.yaml"

        # Copy attachments into attachments/ subdir
        att_dir = folder / "attachments"
        att_dir.mkdir(exist_ok=True)
        copied = []
        for att in attach:
            dest = att_dir / att.name
            shutil.copy2(att, dest)
            copied.append(dest)
    else:
        filename = inbox / f"{prob_id}.yaml"

    filename.write_text(content, encoding="utf-8")

    detail_lines = [f"[green]Created:[/green] {filename}"]
    if use_folder:
        detail_lines.append(f"[green]Attachments:[/green] {len(copied)} file(s) in {att_dir}")
    detail_lines.append(
        f"\n[dim]Next:[/dim] fill in [bold]services[/bold] and [bold]symptoms[/bold], "
        f"then change status to [bold]active[/bold]"
    )

    rprint(Panel(
        "\n".join(detail_lines),
        title=f"[bold]{prob_id}[/bold]",
        border_style="green",
    ))
