"""saab live ..."""

from __future__ import annotations

import typer

app = typer.Typer(help="Live signal streaming, recording, replay")


@app.command()
def stream(signal: list[str], rate: int = 100) -> None:
    """Stream signals to stdout/NDJSON."""
    raise NotImplementedError("live stream not yet implemented")


@app.command()
def record(out: str, bus: str = "all") -> None:
    """Record raw frames to NDJSON."""
    raise NotImplementedError("live record not yet implemented")


@app.command()
def replay(in_file: str, speed: float = 1.0) -> None:
    """Replay a recorded log as a virtual source."""
    raise NotImplementedError("live replay not yet implemented")
