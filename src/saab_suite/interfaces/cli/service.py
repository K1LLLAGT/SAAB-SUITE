from __future__ import annotations

import shutil
import subprocess
import time

import typer

from saab_suite.runtime import paths

app = typer.Typer(help="Termux-native service mode")


def _termux_cmd_exists(cmd: str) -> bool:
    """Return whether a Termux helper command is available."""
    return shutil.which(cmd) is not None


def _run_termux_cmd(cmd: str) -> None:
    """Run a trusted Termux helper when it is available."""
    resolved = shutil.which(cmd)
    if resolved is not None:
        subprocess.run([resolved], check=False)  # noqa: S603


@app.command("run")
def run_service(loop_delay: float = 2.0) -> None:
    """Run a simple long-lived service loop."""
    logs_dir = paths.logs()
    log_file = logs_dir / "service.log"

    if _termux_cmd_exists("termux-wake-lock"):
        _run_termux_cmd("termux-wake-lock")

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
        _run_termux_cmd("termux-wake-unlock")
