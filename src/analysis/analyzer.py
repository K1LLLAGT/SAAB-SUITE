"""
Data analysis tools for SAAB/GM diagnostics.

Provides:
- CAN traffic analysis (message frequencies, anomaly detection).
- DTC aggregation and historical trending.
- Live-data PID charting (requires matplotlib).
- Exporters: CSV, JSON, HTML report.
"""
from __future__ import annotations

import csv
import json
import logging
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CAN traffic analyser
# ---------------------------------------------------------------------------

@dataclass
class MessageStats:
    """Statistics for a single CAN arbitration ID."""
    arb_id: int
    count: int = 0
    first_seen: float = field(default_factory=time.monotonic)
    last_seen: float = field(default_factory=time.monotonic)
    data_lengths: list[int] = field(default_factory=list)
    unique_payloads: set[bytes] = field(default_factory=set)

    @property
    def avg_interval_ms(self) -> Optional[float]:
        if self.count < 2:
            return None
        duration = self.last_seen - self.first_seen
        return round(duration / (self.count - 1) * 1000, 2)

    @property
    def dominant_dlc(self) -> int:
        if not self.data_lengths:
            return 0
        return statistics.mode(self.data_lengths)

    def to_dict(self) -> dict:
        return {
            "arb_id": f"0x{self.arb_id:03X}",
            "count": self.count,
            "avg_interval_ms": self.avg_interval_ms,
            "dominant_dlc": self.dominant_dlc,
            "unique_payloads": len(self.unique_payloads),
        }


class CANAnalyzer:
    """
    Analyse captured CAN frames to identify message patterns, anomalies,
    and protocol traffic.

    Args:
        frames: List of :class:`~can.bus.CANFrame` objects to analyse.
    """

    def __init__(self, frames: Optional[list] = None) -> None:
        self._frames: list = frames or []
        self._stats: dict[int, MessageStats] = {}

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def load_frames(self, frames: list) -> None:
        """Replace internal frame buffer."""
        self._frames = list(frames)
        self._stats.clear()

    def load_csv(self, path: str) -> int:
        """
        Load frames from a CSV file written by :meth:`~can.bus.CANBus.capture`.

        Returns the number of frames loaded.
        """
        loaded = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                from can.bus import CANFrame  # type: ignore
                frame = CANFrame(
                    arbitration_id=int(row["arb_id"], 16),
                    data=bytes(int(b, 16) for b in row["data"].split()),
                    timestamp=float(row["timestamp"]),
                )
                loaded.append(frame)
        self._frames = loaded
        self._stats.clear()
        logger.info("Loaded %d frames from %s", len(loaded), path)
        return len(loaded)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyse(self) -> dict[int, MessageStats]:
        """Process all frames and return per-ID statistics."""
        self._stats.clear()
        for frame in self._frames:
            arb_id = frame.arbitration_id
            if arb_id not in self._stats:
                self._stats[arb_id] = MessageStats(arb_id=arb_id, first_seen=frame.timestamp)
            s = self._stats[arb_id]
            s.count += 1
            s.last_seen = frame.timestamp
            s.data_lengths.append(len(frame.data))
            s.unique_payloads.add(bytes(frame.data))
        return self._stats

    def top_ids(self, n: int = 10) -> list[MessageStats]:
        """Return the *n* most frequent arbitration IDs."""
        if not self._stats:
            self.analyse()
        return sorted(self._stats.values(), key=lambda s: s.count, reverse=True)[:n]

    def detect_anomalies(self, std_multiplier: float = 3.0) -> list[dict]:
        """
        Detect messages whose interval deviates significantly from their mean.

        Args:
            std_multiplier: How many standard deviations beyond the mean
                            constitute an anomaly.

        Returns:
            List of dicts describing anomalous messages.
        """
        if not self._stats:
            self.analyse()

        anomalies = []
        by_id: dict[int, list[float]] = defaultdict(list)
        for frame in self._frames:
            by_id[frame.arbitration_id].append(frame.timestamp)

        for arb_id, timestamps in by_id.items():
            if len(timestamps) < 5:
                continue
            intervals = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
            mean = statistics.mean(intervals)
            stdev = statistics.stdev(intervals)
            if stdev == 0:
                continue
            for i, iv in enumerate(intervals):
                if abs(iv - mean) > std_multiplier * stdev:
                    anomalies.append({
                        "arb_id": f"0x{arb_id:03X}",
                        "frame_index": i,
                        "interval_s": round(iv, 6),
                        "expected_mean_s": round(mean, 6),
                        "deviation_sigma": round((iv - mean) / stdev, 2),
                    })
        return anomalies

    def filter_by_id(self, arb_id: int) -> list:
        """Return frames matching *arb_id*."""
        return [f for f in self._frames if f.arbitration_id == arb_id]

    def protocol_summary(self) -> dict:
        """
        Classify frames by well-known SAAB/GM CAN IDs and return a
        protocol-level summary.
        """
        KNOWN = {
            0x7E0: "ECM request",
            0x7E8: "ECM response",
            0x7E1: "TCM request",
            0x7E9: "TCM response",
            0x7DF: "OBD-II broadcast",
        }
        summary = {}
        for arb_id, label in KNOWN.items():
            frames = self.filter_by_id(arb_id)
            if frames:
                summary[label] = len(frames)
        unknown = sum(
            1 for f in self._frames if f.arbitration_id not in KNOWN
        )
        if unknown:
            summary["unknown/other"] = unknown
        return summary

    # ------------------------------------------------------------------
    # PID trending
    # ------------------------------------------------------------------

    def pid_series(self, arb_id: int, byte_index: int, scale: float = 1.0, offset: float = 0.0) -> list[tuple[float, float]]:
        """
        Extract a time-series from a specific byte of a specific CAN message.

        Args:
            arb_id:     CAN arbitration ID to filter on.
            byte_index: Byte position within the CAN data field.
            scale:      Multiply raw byte value by this factor.
            offset:     Add this offset after scaling.

        Returns:
            List of (timestamp, value) tuples.
        """
        series = []
        for f in self._frames:
            if f.arbitration_id == arb_id and len(f.data) > byte_index:
                value = f.data[byte_index] * scale + offset
                series.append((f.timestamp, value))
        return series

    def plot_pid(self, arb_id: int, byte_index: int, scale: float = 1.0, offset: float = 0.0,
                 title: str = "PID Trend", ylabel: str = "Value", save_path: Optional[str] = None) -> None:
        """
        Plot a PID time-series using matplotlib.

        Args:
            save_path: If given, save the figure to this path instead of
                       displaying interactively.
        """
        try:
            import matplotlib.pyplot as plt  # type: ignore
        except ImportError:
            logger.error("matplotlib is required for plotting. Install with: pip install matplotlib")
            return

        series = self.pid_series(arb_id, byte_index, scale, offset)
        if not series:
            logger.warning("No data for 0x%03X byte %d", arb_id, byte_index)
            return

        timestamps, values = zip(*series)
        t0 = timestamps[0]
        rel_t = [t - t0 for t in timestamps]

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(rel_t, values, linewidth=1.0)
        ax.set_title(f"{title} — 0x{arb_id:03X}[{byte_index}]")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=150)
            logger.info("Plot saved to %s", save_path)
        else:
            plt.show()
        plt.close(fig)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_json(self, path: str) -> None:
        """Export analysis results to a JSON file."""
        if not self._stats:
            self.analyse()
        data = {
            "total_frames": len(self._frames),
            "unique_ids": len(self._stats),
            "messages": [s.to_dict() for s in sorted(self._stats.values(), key=lambda x: x.count, reverse=True)],
        }
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("Analysis exported to %s", path)


# ---------------------------------------------------------------------------
# Diagnostic report
# ---------------------------------------------------------------------------

@dataclass
class DiagnosticReport:
    """
    Aggregates the results of a full vehicle diagnostic scan into a
    structured report that can be rendered to the terminal or exported.

    Args:
        vin:    Vehicle Identification Number.
        ecus:   List of :class:`~engine.core.ECUInfo` found during scan.
        dtcs:   Mapping of ECU address → list of :class:`~engine.diagnostic.DTCCode`.
        pids:   Optional dict of PID name → value for live-data snapshot.
    """

    vin: str = ""
    ecus: list = field(default_factory=list)
    dtcs: dict = field(default_factory=dict)
    pids: dict = field(default_factory=dict)
    scan_time: float = field(default_factory=time.time)

    @property
    def total_dtcs(self) -> int:
        return sum(len(v) for v in self.dtcs.values())

    @property
    def confirmed_dtcs(self) -> list:
        result = []
        for codes in self.dtcs.values():
            result.extend(c for c in codes if c.is_confirmed)
        return result

    def summary(self) -> str:
        lines = [
            f"SAAB-SUITE Diagnostic Report",
            f"{'=' * 40}",
            f"VIN           : {self.vin or 'N/A'}",
            f"ECUs found    : {len(self.ecus)}",
            f"Total DTCs    : {self.total_dtcs}",
            f"Confirmed DTCs: {len(self.confirmed_dtcs)}",
            "",
        ]
        for ecu in self.ecus:
            lines.append(f"  {ecu}")
            for dtc in self.dtcs.get(ecu.address, []):
                lines.append(f"    {dtc}")
        if self.pids:
            lines.append("")
            lines.append("Live Data Snapshot:")
            for name, value in self.pids.items():
                lines.append(f"  {name}: {value}")
        return "\n".join(lines)

    def export_json(self, path: str) -> None:
        """Export the report to a JSON file."""
        data: dict[str, Any] = {
            "vin": self.vin,
            "scan_time": self.scan_time,
            "ecus": [str(e) for e in self.ecus],
            "dtcs": {
                f"0x{addr:02X}": [str(c) for c in codes]
                for addr, codes in self.dtcs.items()
            },
            "pids": self.pids,
        }
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("Report exported to %s", path)

    def export_html(self, path: str) -> None:
        """Export the report to a standalone HTML file."""
        rows = ""
        for ecu in self.ecus:
            dtc_list = self.dtcs.get(ecu.address, [])
            dtc_html = "<br>".join(str(d) for d in dtc_list) if dtc_list else "—"
            rows += f"<tr><td>{ecu}</td><td>{dtc_html}</td></tr>\n"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SAAB-SUITE Diagnostic Report</title>
<style>
  body {{ font-family: monospace; background: #1a1a2e; color: #eee; padding: 2em; }}
  h1   {{ color: #00b4d8; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #444; padding: 0.5em 1em; text-align: left; }}
  th   {{ background: #16213e; color: #90e0ef; }}
  tr:nth-child(even) {{ background: #0f3460; }}
</style>
</head>
<body>
<h1>SAAB-SUITE Diagnostic Report</h1>
<p>VIN: <strong>{self.vin or "N/A"}</strong></p>
<table>
  <thead><tr><th>ECU</th><th>DTCs</th></tr></thead>
  <tbody>
{rows}  </tbody>
</table>
</body>
</html>"""
        Path(path).write_text(html, encoding="utf-8")
        logger.info("HTML report exported to %s", path)
