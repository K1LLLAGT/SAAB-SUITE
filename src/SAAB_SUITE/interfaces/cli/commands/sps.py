"""saab sps ..."""

from __future__ import annotations

import typer

app = typer.Typer(help="SPS -- Service Programming System")


@app.command()
def precheck() -> None:
    """Run precheck against current vehicle."""
    raise NotImplementedError("sps precheck not yet implemented")


@app.command()
def candidates() -> None:
    """List eligible calibrations for the VIN."""
    raise NotImplementedError("sps candidates not yet implemented")


@app.command()
def plan(module: str, cal_id: str) -> None:
    """Build (and print) FlashPlan; dry-run."""
    raise NotImplementedError("sps plan not yet implemented")


@app.command()
def validate(plan_file: str) -> None:
    """Run interlocks against a saved plan."""
    raise NotImplementedError("sps validate not yet implemented")


@app.command()
def flash(plan_file: str, confirm: str = "") -> None:
    """Execute a validated plan. Requires --confirm token."""
    raise NotImplementedError("sps flash not yet implemented")


@app.command()
def compare(cal_a: str, cal_b: str) -> None:
    """Calibration diff."""
    raise NotImplementedError("sps compare not yet implemented")


@app.command()
def recover(session_id: str) -> None:
    """Resume failed flash from session log."""
    raise NotImplementedError("sps recover not yet implemented")
