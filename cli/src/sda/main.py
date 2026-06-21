"""
ArchSpec CLI entry point — Spec-Driven Architecture (SDA).
All commands are registered here.
"""

import typer
from sda.commands.capture import capture
from sda.commands.index import index
from sda.commands.check import check
from sda.commands.scaffold import init
from sda.commands.status import status
from sda.commands.graph import graph as graph_static
from sda.commands.viewer import view as graph_view, serve as graph_serve
from sda.commands.build import build

app = typer.Typer(
    name="sda",
    help="ArchSpec — Spec-Driven Architecture (SDA). Capture problems, record decisions, query your system.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# `graph` is a group: `static` (self-contained single-file), `view` (dockview export),
# `serve` (dockview live server).
graph_app = typer.Typer(
    name="graph",
    help="Render or serve the knowledge-graph viewer.",
    no_args_is_help=True,
)
graph_app.command("static")(graph_static)
graph_app.command("view")(graph_view)
graph_app.command("serve")(graph_serve)

app.command("capture")(capture)
app.command("index")(index)
app.add_typer(graph_app)
app.command("build")(build)
app.command("check")(check)
app.command("init")(init)
app.command("status")(status)


if __name__ == "__main__":
    app()
