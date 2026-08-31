"""saab diag ..."""

from __future__ import annotations

import typer

app = typer.Typer(help="Diagnostics -- DTC read/clear, snapshots")


@app.command()
def dtc(action: str = "read", module: str | None = None) -> None:
    """DTC read or clear."""
    raise NotImplementedError("diag dtc not yet implemented")


@app.command()
def snapshot(module: str, dtc_code: str) -> None:
    """Read freeze frame for a DTC."""
    raise NotImplementedError("diag snapshot not yet implemented")


@app.command()
def identify(module: str) -> None:
    """Read SW/HW/calibration IDs."""
    raise NotImplementedError("diag identify not yet implemented")
