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

app = typer.Typer(
    name="sda",
    help="ArchSpec — Spec-Driven Architecture (SDA). Capture problems, record decisions, query your system.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

app.command("capture")(capture)
app.command("index")(index)
app.command("check")(check)
app.command("init")(init)
app.command("status")(status)


if __name__ == "__main__":
    app()
