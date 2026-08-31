"""saab vehicle ..."""

from __future__ import annotations

import typer

app = typer.Typer(help="Vehicle decode, profile, known issues")


@app.command()
def decode(vin: str) -> None:
    """Decode a VIN and print a summary."""
    raise NotImplementedError("vehicle decode not yet implemented")


@app.command()
def profile(vin: str) -> None:
    """Build and print the VehicleProfile (JSON)."""
    raise NotImplementedError("vehicle profile not yet implemented")


@app.command("known-issues")
def known_issues(vin: str) -> None:
    """List known issues for the given VIN."""
    raise NotImplementedError("known issues not yet implemented")
