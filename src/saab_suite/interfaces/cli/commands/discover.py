"""saab discover ..."""

from __future__ import annotations

import typer

app = typer.Typer(help="Module discovery and topology")


@app.command()
def modules(bus: str = "all") -> None:
    """Probe and list responding modules."""
    raise NotImplementedError("discover modules not yet implemented")


@app.command()
def ping(module: str) -> None:
    """Single module reachability check."""
    raise NotImplementedError("ping not yet implemented")


@app.command()
def topology() -> None:
    """Print expected vs actual topology."""
    raise NotImplementedError("topology not yet implemented")
