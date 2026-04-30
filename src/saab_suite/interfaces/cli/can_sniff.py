from __future__ import annotations

import time

import typer

from saab_suite.runtime import paths

app = typer.Typer(help="CAN bus sniffing tools (mock placeholder)")


@app.command("mock")
def mock_sniff(duration: float = 5.0) -> None:
    """Mock CAN sniffing that just logs timestamps to runtime logs."""
    log_file = paths.logs() / "can_sniff_mock.log"
    start = time.time()
    with log_file.open("a", encoding="utf8") as fh:
        while time.time() - start < duration:
            ts = time.time()
            fh.write(f"{ts:.3f} MOCK_CAN_ID 00000000\n")
            fh.flush()
            time.sleep(0.5)
    typer.echo(f"[CAN] Mock sniff log written to {log_file}")
