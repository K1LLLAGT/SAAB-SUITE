"""``saab`` command entry point."""

from __future__ import annotations

import typer

from saab_suite.__version__ import __version__
from saab_suite.interfaces.cli.commands import (
    can, diag, discover, health, live, sps, tools, vehicle,
)

app = typer.Typer(
    name="saab",
    help="SAAB Programming Suite -- diagnostic and programming for SAAB 9-3 / 9-5",
    no_args_is_help=True,
    add_completion=False,
)
app.add_typer(vehicle.app, name="vehicle")
app.add_typer(discover.app, name="discover")
app.add_typer(diag.app, name="diag")
app.add_typer(live.app, name="live")
app.add_typer(can.app, name="can")
app.add_typer(sps.app, name="sps")
app.add_typer(health.app, name="health")
app.add_typer(tools.app, name="tools")


@app.command()
def version() -> None:
    """Print the suite version and exit."""
    typer.echo(f"saab-suite {__version__}")


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":
    main()
