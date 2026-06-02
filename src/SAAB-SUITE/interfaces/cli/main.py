import typer

app = typer.Typer(help="SAAB-SUITE CLI")

from .commands import (
    can as can_cmd,
    diag as diag_cmd,
    discover as discover_cmd,
    health as health_cmd,
    live as live_cmd,
    sps as sps_cmd,
    tools as tools_cmd,
    vehicle as vehicle_cmd,
)

app.add_typer(can_cmd.app, name="can")
app.add_typer(diag_cmd.app, name="diag")
app.add_typer(discover_cmd.app, name="discover")
app.add_typer(health_cmd.app, name="health")
app.add_typer(live_cmd.app, name="live")
app.add_typer(sps_cmd.app, name="sps")
app.add_typer(tools_cmd.app, name="tools")
app.add_typer(vehicle_cmd.app, name="vehicle")

def main():
    app()

if __name__ == "__main__":
    main()
