"""
sda build — regenerate every derived artifact from source in one step.

Usage:
  sda build            # regenerate architecture/index.yaml + graph.html
  sda build --open     # also open the graph in a browser

A single source edit (e.g. an ADR status change) is reflected everywhere with one
command, instead of running `sda index` then `sda graph` by hand.
"""

from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint

from sda.commands.index import index
from sda.commands.graph import graph, GRAPH_FILE


def build(
    open_browser: Annotated[bool, typer.Option("--open", help="Open the graph in a browser after building")] = False,
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Regenerate all derived artifacts: the knowledge-graph index and the HTML graph."""
    rprint("[bold]Building derived artifacts[/bold]\n")

    rprint("[dim]→ index[/dim]")
    index(validate=False, project_dir=project_dir)

    rprint("\n[dim]→ graph[/dim]")
    graph(output=GRAPH_FILE, html=True, open_browser=open_browser, project_dir=project_dir)

    rprint("\n[green bold]✓ Build complete[/green bold]")
