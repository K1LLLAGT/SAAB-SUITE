"""
SAAB-SUITE full-screen TUI application built with Textual.

Provides a rich, keyboard-driven interface with:
  - A sidebar showing connected ECUs and their DTC counts.
  - A main panel with tabs: Dashboard, DTCs, Live Data, SPS, Logs.
  - A status bar with connection state and vehicle info.

Run with:  python -m tui.app  or  saab-tui
"""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)


def _require_textual():
    try:
        import textual
        return textual
    except ImportError:
        print("The 'textual' package is required for the TUI.  Install with: pip install textual")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

def _build_app(interface: str, protocol: str, baudrate: int):
    """Build and return the Textual App object."""
    _require_textual()

    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.widgets import (
        Button,
        DataTable,
        Footer,
        Header,
        Label,
        Log,
        ProgressBar,
        RichLog,
        Static,
        TabbedContent,
        TabPane,
    )
    from textual.reactive import reactive

    class ECUSidebar(Static):
        """Sidebar listing discovered ECUs."""

        DEFAULT_CSS = """
        ECUSidebar {
            width: 28;
            border: solid cyan;
            padding: 0 1;
        }
        """

        def compose(self) -> ComposeResult:
            yield Label("[bold cyan]ECUs[/bold cyan]")
            yield DataTable(id="ecu_table", show_header=False)

        def on_mount(self) -> None:
            tbl = self.query_one("#ecu_table", DataTable)
            tbl.add_column("ecu", width=24)

        def update_ecus(self, ecus: list) -> None:
            tbl = self.query_one("#ecu_table", DataTable)
            tbl.clear()
            for ecu in ecus:
                tbl.add_row(str(ecu.name))

    class SAABSuiteTUI(App):
        """Full-screen SAAB-SUITE TUI."""

        TITLE = "SAAB-SUITE Diagnostic"
        SUB_TITLE = "Full SAAB/GM Diagnostic Suite"
        CSS_PATH = None

        BINDINGS = [
            Binding("ctrl+c", "quit", "Quit", priority=True),
            Binding("f1", "connect", "Connect"),
            Binding("f2", "discover", "Discover ECUs"),
            Binding("f3", "read_dtcs", "Read DTCs"),
            Binding("f4", "clear_dtcs", "Clear DTCs"),
            Binding("f5", "live_data", "Live Data"),
        ]

        CSS = """
        #main_layout {
            layout: horizontal;
        }
        #content {
            width: 1fr;
        }
        .status_bar {
            height: 1;
            background: $boost;
            color: $text-muted;
            padding: 0 1;
        }
        DataTable {
            height: auto;
        }
        """

        def __init__(self, interface: str, protocol: str, baudrate: int) -> None:
            super().__init__()
            self._interface = interface
            self._protocol = protocol
            self._baudrate = baudrate
            self._engine: Optional[object] = None
            self._ecus: list = []

        def compose(self) -> ComposeResult:
            yield Header()
            with Horizontal(id="main_layout"):
                yield ECUSidebar(id="sidebar")
                with Vertical(id="content"):
                    with TabbedContent():
                        with TabPane("Dashboard", id="tab_dashboard"):
                            yield Static(self._dashboard_text(), id="dashboard_text")
                        with TabPane("DTCs", id="tab_dtcs"):
                            yield DataTable(id="dtc_table")
                        with TabPane("Live Data", id="tab_live"):
                            yield DataTable(id="live_table")
                        with TabPane("SPS", id="tab_sps"):
                            yield Label("[bold]Service Programming System[/bold]")
                            yield Button("Start SPS", id="btn_sps", variant="warning")
                            yield ProgressBar(id="sps_progress", total=100, show_eta=False)
                        with TabPane("Logs", id="tab_logs"):
                            yield RichLog(id="log_view", highlight=True, markup=True)
            yield Footer()

        def on_mount(self) -> None:
            dtc_tbl = self.query_one("#dtc_table", DataTable)
            dtc_tbl.add_columns("ECU", "Code", "Description", "Status")

            live_tbl = self.query_one("#live_table", DataTable)
            live_tbl.add_columns("Parameter", "Value", "Unit")

            self._log("SAAB-SUITE started. Press F1 to connect.")

        # ------------------------------------------------------------------
        # Actions
        # ------------------------------------------------------------------

        def action_connect(self) -> None:
            from engine.core import DiagnosticEngine  # type: ignore
            self._log(f"Connecting via {self._interface}/{self._protocol} …")
            if self._engine:
                self._engine.disconnect()
            self._engine = DiagnosticEngine(
                interface=self._interface,
                protocol=self._protocol,
                baudrate=self._baudrate,
            )
            self._engine.connect()
            self._log("[green]Connected.[/green]")
            self.sub_title = f"Connected | {self._interface}/{self._protocol}"

        def action_discover(self) -> None:
            if not self._engine:
                self._log("[red]Not connected. Press F1 first.[/red]")
                return
            self._log("Discovering ECUs …")
            self._ecus = self._engine.discover_ecus()
            sidebar = self.query_one("#sidebar", ECUSidebar)
            sidebar.update_ecus(self._ecus)
            self._log(f"[green]Found {len(self._ecus)} ECU(s).[/green]")

        def action_read_dtcs(self) -> None:
            if not self._ecus:
                self._log("[red]No ECUs. Press F2 first.[/red]")
                return
            tbl = self.query_one("#dtc_table", DataTable)
            tbl.clear()
            for ecu in self._ecus:
                dtcs = self._engine.read_dtcs(ecu)
                for dtc in dtcs:
                    tbl.add_row(
                        ecu.name,
                        dtc.code_str,
                        dtc.description,
                        "CONFIRMED" if dtc.is_confirmed else "PENDING",
                    )
            self._log(f"[green]DTCs loaded.[/green]")

        def action_clear_dtcs(self) -> None:
            if not self._ecus:
                self._log("[red]No ECUs. Press F2 first.[/red]")
                return
            for ecu in self._ecus:
                self._engine.clear_dtcs(ecu)
            self._log("[yellow]DTCs cleared.[/yellow]")

        def action_live_data(self) -> None:
            if not self._ecus:
                self._log("[red]No ECUs. Press F2 first.[/red]")
                return
            ecu = self._ecus[0]
            tbl = self.query_one("#live_table", DataTable)
            tbl.clear()
            pids = [(0x04, "Engine Load", 100/255, 0, "%"),
                    (0x05, "Coolant Temp", 1, -40, "°C"),
                    (0x0C, "RPM", 0.25, 0, "rpm"),
                    (0x0D, "Vehicle Speed", 1, 0, "km/h"),
                    (0x0F, "Intake Air Temp", 1, -40, "°C"),
                    (0x11, "Throttle Position", 100/255, 0, "%")]
            for pid, name, scale, offset, unit in pids:
                raw = self._engine.read_pid(ecu, pid)
                if raw and len(raw) >= 3:
                    val = f"{raw[2] * scale + offset:.1f}"
                else:
                    val = "—"
                tbl.add_row(name, val, unit)
            self._log("Live data refreshed.")

        # ------------------------------------------------------------------
        # Helpers
        # ------------------------------------------------------------------

        def _log(self, msg: str) -> None:
            log_view = self.query_one("#log_view", RichLog)
            log_view.write(msg)

        @staticmethod
        def _dashboard_text() -> str:
            return (
                "\n[bold cyan]SAAB-SUITE Diagnostic[/bold cyan]\n\n"
                "Keyboard shortcuts:\n"
                "  [bold]F1[/bold]  Connect to vehicle interface\n"
                "  [bold]F2[/bold]  Discover ECUs on vehicle network\n"
                "  [bold]F3[/bold]  Read Diagnostic Trouble Codes\n"
                "  [bold]F4[/bold]  Clear DTCs\n"
                "  [bold]F5[/bold]  Refresh live data snapshot\n\n"
                "Supported vehicles: SAAB 9-3 (2003–2011), 9-5 (1998–2011)\n"
                "Supported protocols: UDS/ISO15765, KWP2000/ISO14230\n"
                "Supported interfaces: J2534, SocketCAN, Kvaser, PEAK, Vector\n"
            )

    return SAABSuiteTUI(interface=interface, protocol=protocol, baudrate=baudrate)


class SAABSuiteTUI:
    """
    Thin public wrapper so that ``from tui.app import SAABSuiteTUI`` works
    even without Textual installed (the import won't fail).
    """

    def __init__(self, interface: str = "j2534", protocol: str = "ISO15765", baudrate: int = 500_000) -> None:
        self.interface = interface
        self.protocol = protocol
        self.baudrate = baudrate

    def run(self) -> None:
        app = _build_app(self.interface, self.protocol, self.baudrate)
        app.run()


def main() -> None:
    """Entry point registered in setup.py."""
    parser = argparse.ArgumentParser(description="SAAB-SUITE full-screen TUI")
    parser.add_argument("--interface", default="j2534")
    parser.add_argument("--protocol", default="ISO15765")
    parser.add_argument("--baudrate", type=int, default=500_000)
    args = parser.parse_args()
    tui = SAABSuiteTUI(interface=args.interface, protocol=args.protocol, baudrate=args.baudrate)
    tui.run()


if __name__ == "__main__":
    main()
