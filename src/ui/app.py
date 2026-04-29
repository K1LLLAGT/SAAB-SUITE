"""
SAAB-SUITE UI application.

Rich-powered terminal application for interactive diagnostics.
Provides menus for ECU discovery, DTC read/clear, live data,
SPS programming, and report export.
"""
from __future__ import annotations

import sys
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _require_rich():
    try:
        import rich
        return rich
    except ImportError:
        print("The 'rich' package is required for the UI.  Install with: pip install rich")
        sys.exit(1)


class SAABSuiteApp:
    """
    Interactive SAAB-SUITE terminal application powered by ``rich``.

    Usage::

        app = SAABSuiteApp()
        app.run()
    """

    BANNER = r"""
[bold cyan]
  ██████  █████  █████  ██████        ███████ ██    ██ ██ ████████ ███████
 ██      ██   ██ ██   ██ ██   ██       ██      ██    ██ ██    ██    ██
  █████  ███████ ███████ ██████  █████ ███████ ██    ██ ██    ██    █████
      ██ ██   ██ ██   ██ ██   ██            ██ ██    ██ ██    ██    ██
 ██████  ██   ██ ██   ██ ██████        ███████  ██████  ██    ██    ███████
[/bold cyan]
[dim]Full SAAB/GM Diagnostic Suite  |  github.com/K1LLLAGT/SAAB-SUITE[/dim]
"""

    MENU_ITEMS = [
        ("1", "Connect / Detect Interface"),
        ("2", "Discover ECUs"),
        ("3", "Read DTCs"),
        ("4", "Clear DTCs"),
        ("5", "Live Data / PIDs"),
        ("6", "Service Programming (SPS)"),
        ("7", "CAN Bus Capture"),
        ("8", "Analyse Captured Data"),
        ("9", "Generate Diagnostic Report"),
        ("G", "Launch GDS2"),
        ("T", "Launch Tech2Win Bridge"),
        ("Q", "Quit"),
    ]

    def __init__(
        self,
        interface: str = "j2534",
        protocol: str = "ISO15765",
        baudrate: int = 500_000,
    ) -> None:
        self.interface = interface
        self.protocol = protocol
        self.baudrate = baudrate

        self._engine: Optional[object] = None
        self._ecus: list = []
        self._last_dtcs: dict = {}

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the interactive menu loop."""
        rich = _require_rich()
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.prompt import Prompt

        self._console = Console()
        self._console.print(self.BANNER)

        while True:
            self._print_menu()
            choice = Prompt.ask("[bold yellow]Select[/bold yellow]").strip().upper()
            self._handle_choice(choice)

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _print_menu(self) -> None:
        from rich.table import Table
        from rich.panel import Panel

        tbl = Table(show_header=False, box=None, padding=(0, 2))
        tbl.add_column("key", style="bold cyan", width=4)
        tbl.add_column("label")
        for key, label in self.MENU_ITEMS:
            tbl.add_row(f"[{key}]", label)

        status = "[green]Connected[/green]" if self._engine else "[red]Disconnected[/red]"
        ecus_str = f"{len(self._ecus)} ECU(s)" if self._ecus else "not scanned"
        self._console.print(Panel(tbl, title=f"SAAB-SUITE  {status}  |  ECUs: {ecus_str}", border_style="cyan"))

    def _handle_choice(self, choice: str) -> None:
        actions = {
            "1": self._action_connect,
            "2": self._action_discover,
            "3": self._action_read_dtcs,
            "4": self._action_clear_dtcs,
            "5": self._action_live_data,
            "6": self._action_sps,
            "7": self._action_capture,
            "8": self._action_analyse,
            "9": self._action_report,
            "G": self._action_gds2,
            "T": self._action_tech2win,
            "Q": self._action_quit,
        }
        action = actions.get(choice)
        if action:
            try:
                action()
            except Exception as exc:  # noqa: BLE001
                self._console.print(f"[red]Error: {exc}[/red]")
        else:
            self._console.print("[yellow]Unknown option.[/yellow]")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _action_connect(self) -> None:
        from rich.prompt import Prompt
        iface = Prompt.ask("Interface", default=self.interface)
        proto = Prompt.ask("Protocol", default=self.protocol)
        from engine.core import DiagnosticEngine  # type: ignore
        if self._engine:
            self._engine.disconnect()
        self._engine = DiagnosticEngine(interface=iface, protocol=proto, baudrate=self.baudrate)
        self._engine.connect()
        self._console.print(f"[green]Connected via {iface}/{proto}[/green]")

    def _action_discover(self) -> None:
        self._require_engine()
        with self._console.status("Discovering ECUs …"):
            self._ecus = self._engine.discover_ecus()
        self._console.print(f"[green]Found {len(self._ecus)} ECU(s).[/green]")
        for ecu in self._ecus:
            self._console.print(f"  • {ecu}")

    def _action_read_dtcs(self) -> None:
        self._require_ecus()
        from rich.table import Table
        tbl = Table(title="Diagnostic Trouble Codes", border_style="red")
        tbl.add_column("ECU", style="cyan")
        tbl.add_column("Code", style="yellow")
        tbl.add_column("Description")
        tbl.add_column("Status", style="dim")

        total = 0
        for ecu in self._ecus:
            dtcs = self._engine.read_dtcs(ecu)
            self._last_dtcs[ecu.address] = dtcs
            for dtc in dtcs:
                tbl.add_row(
                    str(ecu.name),
                    dtc.code_str,
                    dtc.description,
                    "CONFIRMED" if dtc.is_confirmed else "PENDING",
                )
                total += 1
        if total == 0:
            self._console.print("[green]No DTCs found.[/green]")
        else:
            self._console.print(tbl)

    def _action_clear_dtcs(self) -> None:
        self._require_ecus()
        from rich.prompt import Confirm
        if not Confirm.ask("[bold red]Clear ALL DTCs?[/bold red]"):
            return
        for ecu in self._ecus:
            ok = self._engine.clear_dtcs(ecu)
            mark = "[green]✓[/green]" if ok else "[red]✗[/red]"
            self._console.print(f"{mark}  {ecu.name}")

    def _action_live_data(self) -> None:
        self._require_ecus()
        from rich.prompt import IntPrompt
        from rich.table import Table

        ecu = self._ecus[0]
        self._console.print(f"Reading live data from {ecu.name} (Ctrl+C to stop) …")
        pids = [0x04, 0x05, 0x0C, 0x0D, 0x0F, 0x11]  # load, coolant, RPM, speed, IAT, throttle
        labels = ["Engine Load %", "Coolant Temp °C", "RPM", "Speed km/h", "Intake Temp °C", "Throttle %"]
        scales = [100/255, 1, 0.25, 1, 1, 100/255]
        offsets = [0, -40, 0, 0, -40, 0]

        try:
            while True:
                tbl = Table(title="Live Data", border_style="blue")
                tbl.add_column("PID", style="cyan")
                tbl.add_column("Value", style="yellow")
                for pid, label, sc, off in zip(pids, labels, scales, offsets):
                    raw = self._engine.read_pid(ecu, pid)
                    if raw and len(raw) >= 3:
                        val = raw[2] * sc + off
                        tbl.add_row(label, f"{val:.1f}")
                    else:
                        tbl.add_row(label, "—")
                self._console.clear()
                self._console.print(tbl)
                time.sleep(0.5)
        except KeyboardInterrupt:
            self._console.print("[yellow]Live data stopped.[/yellow]")

    def _action_sps(self) -> None:
        self._require_ecus()
        from rich.prompt import Prompt
        cal_path = Prompt.ask("Path to calibration file (.cce / .bin)", default="")
        if not cal_path:
            self._console.print("[yellow]No calibration file provided.[/yellow]")
            return
        from sps.workflow import SPSWorkflow  # type: ignore

        def progress(step: str, pct: int) -> None:
            self._console.print(f"  [cyan]{step}[/cyan] {pct}%")

        ecu = self._ecus[0]
        wf = SPSWorkflow(self._engine, ecu, calibration_path=cal_path, progress_cb=progress)
        result = wf.run()
        if result.success:
            self._console.print(f"[green]{result}[/green]")
        else:
            self._console.print(f"[red]{result}[/red]")

    def _action_capture(self) -> None:
        from rich.prompt import FloatPrompt, Prompt
        duration = FloatPrompt.ask("Capture duration (seconds)", default=10.0)
        output = Prompt.ask("Save to CSV (leave empty to skip)", default="")
        from can.bus import CANBus  # type: ignore
        bus = CANBus()
        with bus:
            frames = bus.capture(duration, output_path=output or None)
        self._console.print(f"[green]Captured {len(frames)} frames.[/green]")

    def _action_analyse(self) -> None:
        from rich.prompt import Prompt
        from analysis.analyzer import CANAnalyzer  # type: ignore
        csv_path = Prompt.ask("CSV file to analyse")
        analyser = CANAnalyzer()
        n = analyser.load_csv(csv_path)
        analyser.analyse()
        self._console.print(f"Loaded {n} frames.")
        top = analyser.top_ids(10)
        from rich.table import Table
        tbl = Table(title="Top 10 CAN IDs", border_style="blue")
        tbl.add_column("Arb ID", style="cyan")
        tbl.add_column("Count", style="yellow")
        tbl.add_column("Avg interval (ms)")
        tbl.add_column("Unique payloads")
        for s in top:
            tbl.add_row(f"0x{s.arb_id:03X}", str(s.count),
                        str(s.avg_interval_ms), str(len(s.unique_payloads)))
        self._console.print(tbl)

    def _action_report(self) -> None:
        from rich.prompt import Prompt
        from analysis.analyzer import DiagnosticReport  # type: ignore
        output = Prompt.ask("Export path (.json or .html)", default="report.html")
        report = DiagnosticReport(
            vin=getattr(self._ecus[0], "vin", "") if self._ecus else "",
            ecus=self._ecus,
            dtcs=self._last_dtcs,
        )
        if output.endswith(".json"):
            report.export_json(output)
        else:
            report.export_html(output)
        self._console.print(f"[green]Report exported to {output}[/green]")

    def _action_gds2(self) -> None:
        from gds2.integration import GDS2Integration  # type: ignore
        gds = GDS2Integration()
        proc = gds.launch()
        if proc:
            self._console.print("[green]GDS2 launched.[/green]")

    def _action_tech2win(self) -> None:
        from gds2.integration import Tech2WinBridge  # type: ignore
        bridge = Tech2WinBridge()
        ok = bridge.start_vm()
        if ok:
            self._console.print("[green]Tech2Win VM started.[/green]")
        else:
            self._console.print("[red]Tech2Win VM could not be started.[/red]")

    def _action_quit(self) -> None:
        if self._engine:
            self._engine.disconnect()
        self._console.print("[cyan]Goodbye.[/cyan]")
        sys.exit(0)

    # ------------------------------------------------------------------
    # Guard helpers
    # ------------------------------------------------------------------

    def _require_engine(self) -> None:
        if not self._engine:
            raise RuntimeError("Not connected. Choose option 1 first.")

    def _require_ecus(self) -> None:
        self._require_engine()
        if not self._ecus:
            raise RuntimeError("No ECUs found. Choose option 2 first.")


def main() -> None:
    """Entry point registered in setup.py."""
    import argparse
    parser = argparse.ArgumentParser(description="SAAB-SUITE interactive diagnostic UI")
    parser.add_argument("--interface", default="j2534", help="J2534 or python-can interface")
    parser.add_argument("--protocol", default="ISO15765", help="Diagnostic protocol")
    parser.add_argument("--baudrate", type=int, default=500_000, help="CAN baudrate")
    args = parser.parse_args()
    app = SAABSuiteApp(interface=args.interface, protocol=args.protocol, baudrate=args.baudrate)
    app.run()


if __name__ == "__main__":
    main()
