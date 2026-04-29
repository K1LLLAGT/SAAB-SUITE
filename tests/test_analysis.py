"""
Tests for data analysis tools (analysis.analyzer).
"""
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from analysis.analyzer import CANAnalyzer, DiagnosticReport, MessageStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_frame(arb_id, data, timestamp=None):
    """Create a lightweight frame-like object for testing without importing CANBus."""
    class _Frame:
        def __init__(self, arb_id, data, ts):
            self.arbitration_id = arb_id
            self.data = data
            self.timestamp = ts
    return _Frame(arb_id, data, time.monotonic() if timestamp is None else timestamp)


def _frames_fixture():
    """Return a small list of test frames."""
    base_ts = 0.0
    frames = []
    for i in range(20):
        frames.append(_make_frame(0x7E8, bytes([i % 256, 0x41, 0x0D, i % 200]), base_ts + i * 0.1))
    for i in range(10):
        frames.append(_make_frame(0x7DF, bytes([0x02, 0x01, 0x0D]), base_ts + i * 0.2))
    frames.append(_make_frame(0x123, bytes([0xFF]), base_ts + 5.0))
    return frames


# ---------------------------------------------------------------------------
# MessageStats
# ---------------------------------------------------------------------------

class TestMessageStats:
    def test_avg_interval_ms_not_enough_data(self):
        ms = MessageStats(arb_id=0x100, count=1)
        assert ms.avg_interval_ms is None

    def test_avg_interval_ms_calculated(self):
        ms = MessageStats(arb_id=0x100, count=3, first_seen=0.0, last_seen=1.0)
        # 2 intervals over 1 second → 500 ms each
        assert ms.avg_interval_ms == pytest.approx(500.0)

    def test_dominant_dlc_empty(self):
        ms = MessageStats(arb_id=0x100)
        assert ms.dominant_dlc == 0

    def test_dominant_dlc(self):
        ms = MessageStats(arb_id=0x100, data_lengths=[8, 8, 8, 4, 8])
        assert ms.dominant_dlc == 8

    def test_to_dict_keys(self):
        ms = MessageStats(arb_id=0x100, count=5)
        d = ms.to_dict()
        assert "arb_id" in d
        assert "count" in d
        assert "avg_interval_ms" in d


# ---------------------------------------------------------------------------
# CANAnalyzer
# ---------------------------------------------------------------------------

class TestCANAnalyzer:
    def test_empty_analyse(self):
        an = CANAnalyzer()
        stats = an.analyse()
        assert stats == {}

    def test_analyse_counts(self):
        frames = _frames_fixture()
        an = CANAnalyzer(frames)
        stats = an.analyse()
        assert stats[0x7E8].count == 20
        assert stats[0x7DF].count == 10
        assert stats[0x123].count == 1

    def test_top_ids(self):
        frames = _frames_fixture()
        an = CANAnalyzer(frames)
        top = an.top_ids(2)
        assert len(top) == 2
        assert top[0].arb_id == 0x7E8  # most frequent

    def test_filter_by_id(self):
        frames = _frames_fixture()
        an = CANAnalyzer(frames)
        filtered = an.filter_by_id(0x7DF)
        assert len(filtered) == 10
        for f in filtered:
            assert f.arbitration_id == 0x7DF

    def test_filter_by_id_no_match(self):
        an = CANAnalyzer(_frames_fixture())
        assert an.filter_by_id(0xABC) == []

    def test_protocol_summary_known_ids(self):
        frames = _frames_fixture()
        an = CANAnalyzer(frames)
        summary = an.protocol_summary()
        assert "ECM response" in summary
        assert "OBD-II broadcast" in summary

    def test_detect_anomalies_no_anomalies(self):
        # Perfectly regular intervals → no anomalies
        frames = [_make_frame(0x7E8, b"\x01", i * 0.1) for i in range(50)]
        an = CANAnalyzer(frames)
        anomalies = an.detect_anomalies(std_multiplier=3.0)
        assert anomalies == []

    def test_detect_anomalies_finds_outlier(self):
        frames = [_make_frame(0x7E8, b"\x01", i * 0.1) for i in range(50)]
        # Inject a large gap at frame 25
        frames.insert(25, _make_frame(0x7E8, b"\x01", 25 * 0.1 + 5.0))
        an = CANAnalyzer(frames)
        anomalies = an.detect_anomalies(std_multiplier=2.0)
        assert len(anomalies) > 0

    def test_pid_series_extracts_values(self):
        frames = [_make_frame(0x7E8, bytes([0x41, 0x0D, i]), i * 0.1) for i in range(10)]
        an = CANAnalyzer(frames)
        series = an.pid_series(arb_id=0x7E8, byte_index=2)
        assert len(series) == 10
        assert series[0][1] == pytest.approx(0.0)
        assert series[9][1] == pytest.approx(9.0)

    def test_pid_series_with_scale_offset(self):
        frames = [_make_frame(0x7E8, bytes([0x41, 0x05, 200]), 0.0)]
        an = CANAnalyzer(frames)
        series = an.pid_series(0x7E8, byte_index=2, scale=1.0, offset=-40)
        assert series[0][1] == pytest.approx(160.0)

    def test_export_json(self, tmp_path):
        an = CANAnalyzer(_frames_fixture())
        output = str(tmp_path / "analysis.json")
        an.export_json(output)
        data = json.loads(Path(output).read_text())
        assert data["total_frames"] == 31
        assert "messages" in data


# ---------------------------------------------------------------------------
# DiagnosticReport
# ---------------------------------------------------------------------------

class TestDiagnosticReport:
    def _make_ecu(self, address, name):
        class _ECU:
            def __init__(self, a, n):
                self.address = a
                self.name = n
                self.vin = "YS3EB49S341001234"
            def __str__(self):
                return f"ECU[0x{self.address:02X}] {self.name}"
        return _ECU(address, name)

    def _make_dtc(self, raw_code, confirmed=True):
        from engine.diagnostic import DTCCode, DTCStatusMask
        status = int(DTCStatusMask.CONFIRMED) if confirmed else int(DTCStatusMask.PENDING)
        return DTCCode(raw_code=raw_code, status=status)

    def test_total_dtcs_empty(self):
        r = DiagnosticReport()
        assert r.total_dtcs == 0

    def test_total_dtcs(self):
        ecu = self._make_ecu(0x7E0, "ECM")
        dtcs = [self._make_dtc(0x0100), self._make_dtc(0x0300, confirmed=False)]
        r = DiagnosticReport(ecus=[ecu], dtcs={0x7E0: dtcs})
        assert r.total_dtcs == 2

    def test_confirmed_dtcs_filters(self):
        ecu = self._make_ecu(0x7E0, "ECM")
        dtcs = [self._make_dtc(0x0100, confirmed=True), self._make_dtc(0x0300, confirmed=False)]
        r = DiagnosticReport(ecus=[ecu], dtcs={0x7E0: dtcs})
        assert len(r.confirmed_dtcs) == 1

    def test_summary_contains_vin(self):
        r = DiagnosticReport(vin="YS3EB49S341001234")
        assert "YS3EB49S341001234" in r.summary()

    def test_export_json(self, tmp_path):
        ecu = self._make_ecu(0x7E0, "ECM")
        r = DiagnosticReport(vin="TEST", ecus=[ecu], dtcs={}, pids={"RPM": 2500})
        output = str(tmp_path / "report.json")
        r.export_json(output)
        data = json.loads(Path(output).read_text())
        assert data["vin"] == "TEST"
        assert data["pids"]["RPM"] == 2500

    def test_export_html(self, tmp_path):
        ecu = self._make_ecu(0x7E0, "ECM")
        r = DiagnosticReport(vin="HTMLTEST", ecus=[ecu], dtcs={})
        output = str(tmp_path / "report.html")
        r.export_html(output)
        html = Path(output).read_text()
        assert "HTMLTEST" in html
        assert "<table" in html
        assert "DOCTYPE" in html
