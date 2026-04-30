from __future__ import annotations

import time
import typer

from saab_suite.runtime.validate import validate_tree
from saab_suite.diag.uds_client import UdsClient

app = typer.Typer(help="Diagnostic tools (UDS, KWP2000, DTC, Live Data, FS)")


# -----------------------------
# UDS
# -----------------------------
uds_app = typer.Typer(help="UDS diagnostics")
app.add_typer(uds_app, name="uds")


@uds_app.command("read")
def uds_read(
    req: str = typer.Option("0x7E0", help="Request CAN ID (e.g. 0x7E0)"),
    res: str = typer.Option("0x7E8", help="Response CAN ID (e.g. 0x7E8)"),
    did: str = typer.Argument(..., help="Data Identifier (e.g. 0xF40C)"),
):
    """UDS ReadDataByIdentifier (0x22)."""
    req_id = int(req, 16)
    res_id = int(res, 16)
    did_val = int(did, 16)

    typer.echo(f"[UDS] 0x22 DID=0x{did_val:04X} REQ=0x{req_id:03X} RES=0x{res_id:03X}")

    try:
        with UdsClient(req_id=req_id, res_id=res_id) as client:
            resp = client.read_data_by_identifier(did_val)
    except TimeoutError:
        typer.echo("[UDS] Timeout waiting for response")
        raise typer.Exit(code=1)

    typer.echo(f"[UDS] Raw response: {resp.raw.hex().upper()}")

    # Simple positive-response check: 0x62 <DID_hi> <DID_lo> ...
    if len(resp.raw) >= 3 and resp.raw[0] == 0x62:
        resp_did = (resp.raw[1] << 8) | resp.raw[2]
        if resp_did == did_val:
            data_bytes = resp.raw[3:]
            typer.echo(f"[UDS] Data bytes: {data_bytes.hex().upper()}")
        else:
            typer.echo(f"[UDS] DID mismatch in response: 0x{resp_did:04X}")
    else:
        typer.echo("[UDS] Non-positive or unexpected response")


# -----------------------------
# KWP2000 (still mock for now)
# -----------------------------
kwp_app = typer.Typer(help="KWP2000 diagnostics")
app.add_typer(kwp_app, name="kwp")


@kwp_app.command("read-dtc")
def kwp_read_dtc():
    typer.echo("[KWP] Reading DTCs (mock)...")
    typer.echo("P1312 - Cylinder 1 Knock")
    typer.echo("P1334 - Cylinder 2 Knock")


# -----------------------------
# Live data (mock)
# -----------------------------
@app.command("live")
def live_data(duration: float = 5.0):
    typer.echo("[LIVE] Streaming mock live data...")
    start = time.time()
    while time.time() - start < duration:
        ts = time.time()
        rpm = 800 + int((ts * 10) % 300)
        boost = 0.5 + ((ts * 0.1) % 0.3)
        typer.echo(f"{ts:.3f} RPM={rpm} BOOST={boost:.2f}bar")
        time.sleep(0.5)


# -----------------------------
# FS validator
# -----------------------------
@app.command("fs")
def fs_check():
    """Validate runtime directory tree."""
    for status in validate_tree():
        ok = status.exists and status.is_dir
        flag = "OK" if ok else "FAIL"
        typer.echo(f"[FS] {flag} {status.name}: {status.path}")
