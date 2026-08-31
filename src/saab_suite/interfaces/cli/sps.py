from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import Annotated

import typer

from saab_suite.runtime import paths

app = typer.Typer(help="SPS flash preparation wizard")


@app.command("prepare")
def prepare(
    vin: Annotated[str, typer.Option(help="Vehicle VIN")],
    module: Annotated[str, typer.Option(help="Target module (e.g. T8, CIM, ABS)")],
    file: Annotated[
        Path | None,
        typer.Option(
            exists=True,
            dir_okay=False,
            help="Calibration/flash file (defaults to runtime SPS directory)",
        ),
    ] = None,
) -> None:
    """Prepare SPS flash session (dry-run)."""
    sps_dir = paths.sps()
    if file is None:
        typer.echo(f"[INFO] SPS directory: {sps_dir}")
        typer.echo("[ERROR] No file specified. Place files in SPS directory or pass --file.")
        raise typer.Exit(code=1)

    typer.echo(f"[SPS] VIN: {vin}")
    typer.echo(f"[SPS] Module: {module}")
    typer.echo(f"[SPS] File: {file}")
    typer.echo("[SPS] Running sanity checks (placeholder)...")
    typer.echo("[SPS] OK: ready for flash (simulation).")
