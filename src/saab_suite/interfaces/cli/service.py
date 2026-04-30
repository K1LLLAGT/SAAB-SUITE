from __future__ import annotations

import subprocess
import time

import typer

from saab_suite.runtime import paths

app = typer.Typer(help="Termux-native service mode")


def _termux_cmd_exists(cmd: str) -> bool:
    return subprocess.call(
        ["command", "-v", cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) == 0


@app.command("run")
def run_service(loop_delay: float = 2.0) -> None:
    """Run a simple long-lived service loop."""
    logs_dir = paths.logs()
    log_file = logs_dir / "service.log"

    if _termux_cmd_exists("termux-wake-lock"):
        subprocess.call(["termux-wake-lock"])

    with log_file.open("a", encoding="utf8") as fh:
        fh.write("[SERVICE] Started service loop\n")
        fh.flush()
        try:
            while True:
                fh.write("[SERVICE] Heartbeat\n")
                fh.flush()
                time.sleep(loop_delay)
        except KeyboardInterrupt:
            fh.write("[SERVICE] Stopped by user\n")
            fh.flush()

    if _termux_cmd_exists("termux-wake-unlock"):
        subprocess.call(["termux-wake-unlock"])
