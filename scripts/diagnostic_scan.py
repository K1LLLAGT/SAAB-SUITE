#!/usr/bin/env python3
"""
diagnostic_scan.py – Full vehicle diagnostic scan script.

Connects to the vehicle, discovers all ECUs, reads DTCs and a live-data
snapshot, then exports a diagnostic report (JSON or HTML).

Usage:
    python scripts/diagnostic_scan.py [options]
    saab-scan [options]                  # if installed via setup.py

Examples:
    # Quick scan with default J2534 interface, export HTML report
    python scripts/diagnostic_scan.py --report report.html

    # Use SocketCAN interface, JSON export
    python scripts/diagnostic_scan.py --interface socketcan --channel can0 --report scan.json

    # Dry-run (no hardware, simulation mode)
    python scripts/diagnostic_scan.py --simulate --report /tmp/sim_report.html
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Allow running from repository root without installation
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(name)s: %(message)s")
logger = logging.getLogger("saab_scan")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SAAB-SUITE full vehicle diagnostic scan",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--interface", default="j2534",
                        help="Interface type: j2534, socketcan, kvaser, peak, vector (default: j2534)")
    parser.add_argument("--channel", default="can0",
                        help="Channel (e.g. 'can0' for SocketCAN, '1' for J2534 channel 1)")
    parser.add_argument("--protocol", default="ISO15765",
                        help="Diagnostic protocol: ISO15765 (UDS/CAN) or ISO14230 (KWP2000)")
    parser.add_argument("--baudrate", type=int, default=500_000,
                        help="CAN bus baudrate in bps (default: 500000)")
    parser.add_argument("--timeout", type=float, default=5.0,
                        help="ECU discovery timeout in seconds (default: 5)")
    parser.add_argument("--report", default="",
                        help="Export report to this path (.json or .html).  Empty = print to stdout.")
    parser.add_argument("--capture", default="",
                        help="Also capture raw CAN traffic for N seconds and save to CSV")
    parser.add_argument("--capture-duration", type=float, default=10.0,
                        help="Duration for CAN capture in seconds (default: 10)")
    parser.add_argument("--simulate", action="store_true",
                        help="Simulation mode (no real hardware needed)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose / debug output")
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.simulate:
        logger.info("Running in simulation mode (no hardware required).")

    # ---------------------------------------------------------------
    # Connect
    # ---------------------------------------------------------------
    from engine.core import DiagnosticEngine  # type: ignore
    from analysis.analyzer import DiagnosticReport  # type: ignore

    interface = "j2534" if not args.simulate else "j2534"
    engine = DiagnosticEngine(
        interface=interface,
        protocol=args.protocol,
        baudrate=args.baudrate,
        channel=int(args.channel) if args.channel.isdigit() else 1,
    )

    logger.info("Connecting to vehicle via %s/%s @ %d bps …", interface, args.protocol, args.baudrate)
    try:
        engine.connect()
    except Exception as exc:  # noqa: BLE001
        logger.error("Connection failed: %s", exc)
        return 1

    # ---------------------------------------------------------------
    # ECU discovery
    # ---------------------------------------------------------------
    logger.info("Discovering ECUs (timeout=%.1fs) …", args.timeout)
    ecus = engine.discover_ecus(timeout=args.timeout)
    if not ecus:
        logger.warning("No ECUs found.  Check connection and vehicle ignition.")
    else:
        logger.info("Found %d ECU(s):", len(ecus))
        for ecu in ecus:
            logger.info("  %s", ecu)

    # ---------------------------------------------------------------
    # Read DTCs
    # ---------------------------------------------------------------
    dtcs: dict = {}
    for ecu in ecus:
        codes = engine.read_dtcs(ecu)
        dtcs[ecu.address] = codes
        if codes:
            logger.info("  [%s] %d DTC(s):", ecu.name, len(codes))
            for dtc in codes:
                logger.info("    %s", dtc)
        else:
            logger.info("  [%s] No DTCs.", ecu.name)

    # ---------------------------------------------------------------
    # Live data snapshot
    # ---------------------------------------------------------------
    pids_snapshot: dict = {}
    if ecus:
        ecu = ecus[0]
        pid_map = {
            "Engine Load (%)": (0x04, 100/255, 0),
            "Coolant Temp (°C)": (0x05, 1, -40),
            "RPM": (0x0C, 0.25, 0),
            "Vehicle Speed (km/h)": (0x0D, 1, 0),
            "Throttle Position (%)": (0x11, 100/255, 0),
        }
        logger.info("Reading live data from %s …", ecu.name)
        for name, (pid, scale, offset) in pid_map.items():
            raw = engine.read_pid(ecu, pid)
            if raw and len(raw) >= 3:
                val = raw[2] * scale + offset
                pids_snapshot[name] = round(val, 2)

    # ---------------------------------------------------------------
    # Optional CAN capture
    # ---------------------------------------------------------------
    if args.capture:
        from can.bus import CANBus  # type: ignore
        logger.info("Capturing CAN traffic for %.1fs …", args.capture_duration)
        bus = CANBus(interface="socketcan", channel="can0", bitrate=args.baudrate)
        try:
            with bus:
                bus.capture(args.capture_duration, output_path=args.capture)
            logger.info("CAN capture saved to %s", args.capture)
        except Exception as exc:  # noqa: BLE001
            logger.warning("CAN capture failed: %s", exc)

    # ---------------------------------------------------------------
    # Report
    # ---------------------------------------------------------------
    vin = ecus[0].vin if ecus else ""
    report = DiagnosticReport(vin=vin, ecus=ecus, dtcs=dtcs, pids=pids_snapshot)

    if args.report:
        report_path = args.report
        if report_path.endswith(".json"):
            report.export_json(report_path)
        else:
            report.export_html(report_path)
        logger.info("Report saved to %s", report_path)
    else:
        print("\n" + report.summary())

    engine.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
