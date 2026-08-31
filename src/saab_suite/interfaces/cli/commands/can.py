"""saab can ..."""

from __future__ import annotations

import typer

app = typer.Typer(help="CAN sniff, decode, info")


@app.command()
def sniff(bus: str = "all", filter: str | None = None) -> None:
    """Raw frame dump."""
    raise NotImplementedError("can sniff not yet implemented")


@app.command()
def decode(log: str) -> None:
    """Decode a log via DBC."""
    raise NotImplementedError("can decode not yet implemented")


@app.command()
def info() -> None:
    """Show DBC index summary."""
    raise NotImplementedError("can info not yet implemented")
