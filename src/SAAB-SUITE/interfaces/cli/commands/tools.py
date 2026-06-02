"""saab tools ..."""

from __future__ import annotations

import typer

app = typer.Typer(help="Diagnostic tooling and environment validation")


j2534_app = typer.Typer(help="J2534 device tools")
env_app = typer.Typer(help="Environment validation")
app.add_typer(j2534_app, name="j2534")
app.add_typer(env_app, name="env")


@j2534_app.command("list")
def j2534_list() -> None:
    """Enumerate J2534 devices."""
    raise NotImplementedError("j2534 list not yet implemented")


@j2534_app.command("info")
def j2534_info(device: str) -> None:
    """Show device capabilities."""
    raise NotImplementedError("j2534 info not yet implemented")


@env_app.command("validate")
def env_validate() -> None:
    """Check runtime preconditions."""
    raise NotImplementedError("env validate not yet implemented")
