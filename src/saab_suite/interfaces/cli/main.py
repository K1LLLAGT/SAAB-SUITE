import typer

from .commands import (
    can as can_cmd,
)
from .commands import (
    diag as diag_cmd,
)
from .commands import (
    discover as discover_cmd,
)
from .commands import (
    health as health_cmd,
)
from .commands import (
    live as live_cmd,
)
from .commands import (
    sps as sps_cmd,
)
from .commands import (
    tools as tools_cmd,
)
from .commands import (
    vehicle as vehicle_cmd,
)

app = typer.Typer(help="saab_suite CLI")

app.add_typer(can_cmd.app, name="can")
app.add_typer(diag_cmd.app, name="diag")
app.add_typer(discover_cmd.app, name="discover")
app.add_typer(health_cmd.app, name="health")
app.add_typer(live_cmd.app, name="live")
app.add_typer(sps_cmd.app, name="sps")
app.add_typer(tools_cmd.app, name="tools")
app.add_typer(vehicle_cmd.app, name="vehicle")

def main() -> None:
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    main()
