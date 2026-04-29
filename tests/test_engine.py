"""
Tests for the diagnostic engine (engine.core, engine.diagnostic).
"""
import sys
from pathlib import Path

# Allow imports from src/ without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from engine.core import DiagnosticEngine, ECUInfo, _NullBus
from engine.diagnostic import DTCCode, DTCStatusMask, DiagnosticSession, SessionType


# ---------------------------------------------------------------------------
# ECUInfo
# ---------------------------------------------------------------------------

class TestECUInfo:
    def test_str_format(self):
        ecu = ECUInfo(address=0x7E0, name="ECM", software_version="1.2.3")
        s = str(ecu)
        assert "7E0" in s
        assert "ECM" in s
        assert "1.2.3" in s

    def test_defaults(self):
        ecu = ECUInfo(address=0x7E1, name="TCM")
        assert ecu.software_version == "unknown"
        assert ecu.vin == ""


# ---------------------------------------------------------------------------
# DiagnosticEngine
# ---------------------------------------------------------------------------

class TestDiagnosticEngine:
    def test_connect_disconnect(self):
        eng = DiagnosticEngine(interface="socketcan")
        eng.connect()
        assert eng._connected
        eng.disconnect()
        assert not eng._connected

    def test_context_manager(self):
        with DiagnosticEngine(interface="socketcan") as eng:
            assert eng._connected
        assert not eng._connected

    def test_double_connect_is_safe(self):
        eng = DiagnosticEngine()
        eng.connect()
        eng.connect()  # should not raise
        eng.disconnect()

    def test_disconnect_when_not_connected_is_safe(self):
        eng = DiagnosticEngine()
        eng.disconnect()  # should not raise

    def test_require_connected_raises(self):
        eng = DiagnosticEngine()
        with pytest.raises(RuntimeError, match="not connected"):
            eng.discover_ecus()

    def test_read_dtcs_no_hardware(self):
        """Engine with NullBus returns empty DTC list."""
        eng = DiagnosticEngine()
        eng._connected = True
        eng._bus = _NullBus()
        ecu = ECUInfo(address=0x7E0, name="ECM")
        dtcs = eng.read_dtcs(ecu)
        assert dtcs == []

    def test_clear_dtcs_no_hardware(self):
        eng = DiagnosticEngine()
        eng._connected = True
        eng._bus = _NullBus()
        ecu = ECUInfo(address=0x7E0, name="ECM")
        result = eng.clear_dtcs(ecu)
        assert result is False

    def test_discover_ecus_no_hardware(self):
        eng = DiagnosticEngine()
        eng._connected = True
        eng._bus = _NullBus()
        ecus = eng.discover_ecus(timeout=0.1)
        assert isinstance(ecus, list)

    def test_known_ecus_populated(self):
        assert 0x7E0 in DiagnosticEngine.KNOWN_ECUS
        assert DiagnosticEngine.KNOWN_ECUS[0x7E0].startswith("ECM")


# ---------------------------------------------------------------------------
# DTCCode
# ---------------------------------------------------------------------------

class TestDTCCode:
    def test_code_str_p_code(self):
        dtc = DTCCode(raw_code=0x0100)
        assert dtc.code_str == "P0100"

    def test_code_str_b_code(self):
        dtc = DTCCode(raw_code=0x8300)  # B category = bits 15-14 = 10 → index 2 = B
        # raw_code 0x8300: bits 15-14 = 10 (binary) → category index 2 → "B"
        assert dtc.code_str.startswith("B")

    def test_description_known(self):
        dtc = DTCCode(raw_code=0x0100)
        assert "Air Flow" in dtc.description

    def test_description_unknown(self):
        dtc = DTCCode(raw_code=0x9999)
        assert "Unknown" in dtc.description

    def test_is_confirmed(self):
        dtc = DTCCode(raw_code=0x0100, status=int(DTCStatusMask.CONFIRMED))
        assert dtc.is_confirmed

    def test_is_not_confirmed(self):
        dtc = DTCCode(raw_code=0x0100, status=int(DTCStatusMask.PENDING))
        assert not dtc.is_confirmed

    def test_is_pending(self):
        dtc = DTCCode(raw_code=0x0100, status=int(DTCStatusMask.PENDING))
        assert dtc.is_pending

    def test_str_confirmed(self):
        dtc = DTCCode(raw_code=0x0100, status=int(DTCStatusMask.CONFIRMED))
        assert "CONFIRMED" in str(dtc)

    def test_str_pending(self):
        dtc = DTCCode(raw_code=0x0100, status=int(DTCStatusMask.PENDING))
        assert "PENDING" in str(dtc)

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def test_parse_uds_response_empty(self):
        assert DTCCode.parse_uds_response(b"") == []

    def test_parse_uds_response_wrong_sid(self):
        assert DTCCode.parse_uds_response(b"\x19\x02\xFF\x00\x01\x00\x08") == []

    def test_parse_uds_response_single_dtc(self):
        # 0x59 0x02 0xFF [DTC: 0x00 0x01 0x00] [status: 0x08]
        data = bytes([0x59, 0x02, 0xFF, 0x00, 0x01, 0x00, 0x08])
        codes = DTCCode.parse_uds_response(data)
        assert len(codes) == 1
        assert codes[0].status == 0x08
        assert codes[0].is_confirmed

    def test_parse_uds_response_multiple_dtcs(self):
        data = bytes([0x59, 0x02, 0xFF,
                      0x00, 0x01, 0x00, 0x08,
                      0x00, 0x03, 0x00, 0x04])
        codes = DTCCode.parse_uds_response(data)
        assert len(codes) == 2


# ---------------------------------------------------------------------------
# DiagnosticSession
# ---------------------------------------------------------------------------

class TestDiagnosticSession:
    def _make_session(self, session_type=SessionType.DEFAULT):
        eng = DiagnosticEngine()
        eng._connected = True
        eng._bus = _NullBus()
        ecu = ECUInfo(address=0x7E0, name="ECM")
        return DiagnosticSession(engine=eng, ecu=ecu, session_type=session_type)

    def test_open_fails_null_bus(self):
        session = self._make_session(SessionType.EXTENDED_DIAGNOSTIC)
        # NullBus returns None → open should raise RuntimeError
        with pytest.raises(RuntimeError):
            session.open()

    def test_close_when_not_open_is_safe(self):
        session = self._make_session()
        session.close()  # should not raise

    def test_context_manager_raises_on_null_bus(self):
        session = self._make_session(SessionType.EXTENDED_DIAGNOSTIC)
        with pytest.raises(RuntimeError):
            with session:
                pass

    def test_unlock_security_raises_when_closed(self):
        session = self._make_session()
        with pytest.raises(RuntimeError, match="must be open"):
            session.unlock_security()
