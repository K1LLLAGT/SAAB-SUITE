"""saab health ..."""

from __future__ import annotations

import typer

app = typer.Typer(help="Vehicle health reports")


@app.command()
def report(out: str = "md") -> None:
    """Generate health report."""
    raise NotImplementedError("health report not yet implemented")


@app.command()
def haldex() -> None:
    """XWD/Haldex-specific report."""
    raise NotImplementedError("haldex report not yet implemented")
