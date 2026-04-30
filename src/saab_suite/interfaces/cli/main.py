from __future__ import annotations

import typer

from saab_suite.interfaces.cli.sps import app as sps_app
from saab_suite.interfaces.cli.service import app as service_app
from saab_suite.interfaces.cli.can_sniff import app as can_sniff_app
from saab_suite.interfaces.cli.diag import app as diag_app
from saab_suite.vin.decoder import decode_vin
from saab_suite.adapters.can.replay_source import ReplayCanSource
from saab_suite.adapters.can.remote_interface import RemoteCanInterface, CanFrame
from saab_suite.plugins.loader import load_plugins

app = typer.Typer(help="SAAB Suite – Main CLI")

app.add_typer(sps_app, name="sps")
app.add_typer(service_app, name="service")
app.add_typer(can_sniff_app, name="sniff")
app.add_typer(diag_app, name="diag")


@app.command("vin")
def vin_cmd(vin: str):
    info = decode_vin(vin)
    if not info:
        typer.echo("[VIN] Unknown or invalid VIN")
        raise typer.Exit(code=1)

    typer.echo(f"[VIN] {info.vin}")
    typer.echo(f"  Model:  {info.model}")
    typer.echo(f"  Year:   {info.year}")
    typer.echo(f"  Engine: {info.engine}")


@app.command("replay")
def replay_cmd(name: str):
    src = ReplayCanSource.from_name(name)
    for frame in src:
        typer.echo(f"{frame.timestamp:.3f} {frame.can_id:08X} {frame.data.hex().upper()}")


@app.command("can-test")
def can_test():
    iface = RemoteCanInterface()
    iface.open()
    try:
        typer.echo("[CAN] Mode test...")
        iface.send(CanFrame(can_id=0x7DF, data=b"\x01\x00\x00\x00\x00\x00\x00\x00"))
        typer.echo("[CAN] Waiting for response...")
        frame = iface.recv(timeout=1.0)
        if frame is None:
            typer.echo("[CAN] No response (timeout)")
        else:
            typer.echo(f"[CAN] RX {frame.can_id:08X} {frame.data.hex().upper()}")
    finally:
        iface.close()


plugins_app = typer.Typer(help="Plugin management")
app.add_typer(plugins_app, name="plugins")


@plugins_app.command("list")
def plugins_list():
    plugins = load_plugins()
    if not plugins:
        typer.echo("[PLUGINS] No plugins loaded")
        return
    for p in plugins:
        typer.echo(f"- {p.name}")


@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo("SAAB Suite CLI – use --help for commands")


def main():
    app()
