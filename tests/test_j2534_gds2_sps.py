"""
Tests for J2534 interface, GDS2 integration, and SPS workflow.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from j2534.interface import J2534Interface, J2534Error, PassThruChannel, Protocol
from gds2.integration import GDS2Integration, Tech2WinBridge
from sps.workflow import SPSWorkflow, SPSError, ProgrammingStep


# ---------------------------------------------------------------------------
# J2534
# ---------------------------------------------------------------------------

class TestJ2534Error:
    def test_known_code(self):
        err = J2534Error(0x07, "test")
        assert "ERR_FAILED" in str(err)
        assert "test" in str(err)

    def test_unknown_code(self):
        err = J2534Error(0xFF)
        assert "UNKNOWN_ERROR" in str(err)


class TestJ2534Interface:
    def test_simulation_mode_on_non_windows(self):
        iface = J2534Interface()
        iface.open()
        assert iface._simulation_mode

    def test_connect_channel_simulation(self):
        iface = J2534Interface()
        iface.open()
        ch = iface.connect_to_channel()
        assert isinstance(ch, PassThruChannel)
        assert ch.channel_id == 1

    def test_send_uds_simulation_returns_positive_response(self):
        iface = J2534Interface()
        iface.open()
        # Simulation mode echoes SID | 0x40 as positive response
        response = iface.send_uds(0x7E0, b"\x3E\x00")
        assert response is not None
        assert response[0] == (0x3E | 0x40)

    def test_send_uds_simulation_empty_payload(self):
        iface = J2534Interface()
        iface.open()
        assert iface.send_uds(0x7E0, b"") is None

    def test_protocol_id_iso15765(self):
        assert J2534Interface._protocol_id("ISO15765") == Protocol.ISO15765

    def test_protocol_id_kwp2000_alias(self):
        assert J2534Interface._protocol_id("KWP2000") == Protocol.ISO14230

    def test_protocol_id_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown J2534 protocol"):
            J2534Interface._protocol_id("BOGUS")

    def test_check_no_error(self):
        J2534Interface._check(0, "test")  # should not raise

    def test_check_error_raises(self):
        with pytest.raises(J2534Error):
            J2534Interface._check(0x07, "test")

    def test_find_dll_non_windows_returns_none(self):
        # On non-Windows, registry is not available → None
        result = J2534Interface._find_dll()
        assert result is None

    def test_context_manager(self):
        with J2534Interface() as iface:
            assert iface._simulation_mode

    def test_shutdown_alias(self):
        iface = J2534Interface()
        iface.open()
        iface.shutdown()  # should not raise


class TestPassThruChannel:
    def _make_channel(self):
        iface = J2534Interface()
        iface.open()
        return iface.connect_to_channel()

    def test_send_uds_returns_response(self):
        ch = self._make_channel()
        resp = ch.send_uds(0x7E0, b"\x22\xF1\x90")
        assert resp is not None

    def test_context_manager(self):
        iface = J2534Interface()
        iface.open()
        with iface.connect_to_channel() as ch:
            assert ch.channel_id == 1


# ---------------------------------------------------------------------------
# GDS2Integration
# ---------------------------------------------------------------------------

class TestGDS2Integration:
    def test_detect_installation_missing(self):
        gds = GDS2Integration(install_dir="/nonexistent/path/gds2")
        assert gds.detect_installation() is None

    def test_detect_installation_custom_path(self, tmp_path):
        gds = GDS2Integration(install_dir=str(tmp_path))
        result = gds.detect_installation()
        assert result == tmp_path

    def test_launch_no_installation(self):
        gds = GDS2Integration(install_dir="/nonexistent")
        proc = gds.launch()
        assert proc is None

    def test_get_version_no_installation(self):
        gds = GDS2Integration(install_dir="/nonexistent")
        assert gds.get_version() is None


class TestTech2WinBridge:
    def test_find_vm_default_missing(self):
        bridge = Tech2WinBridge()
        assert bridge.find_vm() is None

    def test_find_vm_custom_path(self, tmp_path):
        vmx = tmp_path / "test.vmx"
        vmx.write_text("VMX config")
        bridge = Tech2WinBridge(vm_path=str(vmx))
        assert bridge.find_vm() == vmx

    def test_start_vm_no_vm(self):
        bridge = Tech2WinBridge(vm_path="/nonexistent/test.vmx")
        result = bridge.start_vm()
        assert result is False

    def test_vm_status_no_vm(self):
        bridge = Tech2WinBridge()
        status = bridge.vm_status()
        assert status in ("running", "stopped", "unknown")


# ---------------------------------------------------------------------------
# SPS Workflow
# ---------------------------------------------------------------------------

class TestProgrammingStep:
    def test_str_pending(self):
        step = ProgrammingStep("test", "A test step")
        s = str(step)
        assert "test" in s
        assert "pending" in s

    def test_str_completed(self):
        step = ProgrammingStep("test", "A test step", completed=True)
        s = str(step)
        assert "✓" in s


class TestSPSWorkflow:
    def _make_workflow(self, cal_path=None):
        """Create a workflow using the NullBus engine."""
        from engine.core import DiagnosticEngine, ECUInfo, _NullBus
        eng = DiagnosticEngine()
        eng._connected = True
        eng._bus = _NullBus()
        ecu = ECUInfo(address=0x7E0, name="ECM")
        return SPSWorkflow(engine=eng, ecu=ecu, calibration_path=cal_path)

    def test_steps_defined(self):
        wf = self._make_workflow()
        assert len(wf.steps) > 0
        names = [s.name for s in wf.steps]
        assert "preconditions" in names
        assert "open_session" in names
        assert "download_calibration" in names

    def test_run_no_calibration_file_fails_gracefully(self, tmp_path):
        wf = self._make_workflow(cal_path=str(tmp_path / "nonexistent.cce"))
        result = wf.run()
        # Should fail at preconditions (file not found)
        assert not result.success
        assert "not found" in result.message.lower()

    def test_run_with_calibration_file(self, tmp_path):
        cal = tmp_path / "test.cce"
        cal.write_bytes(bytes(range(256)))  # 256-byte dummy calibration
        wf = self._make_workflow(cal_path=str(cal))
        result = wf.run()
        # NullBus → programming session will fail
        assert isinstance(result.success, bool)

    def test_progress_callback_called(self, tmp_path):
        cal = tmp_path / "test.cce"
        cal.write_bytes(b"\x00" * 64)
        events = []
        wf = self._make_workflow(cal_path=str(cal))
        wf.progress_cb = lambda step, pct: events.append((step, pct))
        wf.run()
        assert len(events) > 0

    def test_result_str_success(self):
        from sps.workflow import ProgrammingResult
        r = ProgrammingResult(
            success=True,
            ecu_address=0x7E0,
            calibration_id_before="A",
            calibration_id_after="B",
            steps=[],
            duration_s=12.3,
        )
        assert "SUCCESS" in str(r)
        assert "7E0" in str(r)

    def test_result_str_failed(self):
        from sps.workflow import ProgrammingResult
        r = ProgrammingResult(
            success=False,
            ecu_address=0x7E0,
            calibration_id_before="A",
            calibration_id_after="A",
            steps=[],
            duration_s=1.0,
            message="Precondition failed",
        )
        assert "FAILED" in str(r)
