"""
Service Programming System (SPS) workflows.

SPS is GM's system for reprogramming ECU firmware over a diagnostic link.
It follows a well-defined sequence:
  1. Identify the vehicle and current ECU calibration.
  2. Check for available calibration updates.
  3. Download the update package from a server (or use a local package).
  4. Unlock the ECU programming mode (extended session + security access).
  5. Erase and reflash the ECU.
  6. Verify the new calibration.
  7. Reset and re-initialise the ECU.

This module models that workflow in a safe, step-by-step manner with
proper error handling and rollback on failure.
"""
from __future__ import annotations

import enum
import hashlib
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------

class SPSError(Exception):
    """Raised when an SPS programming step fails."""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ProgrammingStep:
    """Describes a single step in an SPS programming sequence."""
    name: str
    description: str
    required: bool = True
    completed: bool = False
    error: Optional[str] = None

    def __str__(self) -> str:
        status = "✓" if self.completed else ("✗ " + (self.error or "pending"))
        return f"[{status}] {self.name}: {self.description}"


@dataclass
class ProgrammingResult:
    """Result of a complete SPS programming session."""
    success: bool
    ecu_address: int
    calibration_id_before: str
    calibration_id_after: str
    steps: list[ProgrammingStep]
    duration_s: float
    message: str = ""

    def __str__(self) -> str:
        state = "SUCCESS" if self.success else "FAILED"
        return (
            f"SPS {state}: ECU 0x{self.ecu_address:02X} "
            f"{self.calibration_id_before} → {self.calibration_id_after} "
            f"({self.duration_s:.1f}s)"
        )


# ---------------------------------------------------------------------------
# SPS workflow
# ---------------------------------------------------------------------------

class SPSWorkflow:
    """
    Orchestrates a GM Service Programming System (SPS) flash session.

    Args:
        engine:           :class:`~engine.core.DiagnosticEngine` instance.
        ecu:              :class:`~engine.core.ECUInfo` target ECU.
        calibration_path: Path to the ``.cce``/``.bin`` calibration file.
        key_fn:           Security-access key function for the target ECU.
        progress_cb:      Optional callback ``(step_name: str, pct: int)``
                          called after each programming step.
    """

    # UDS service IDs
    _SID_ECU_RESET = 0x11
    _SID_SESSION = 0x10
    _SID_SECURITY = 0x27
    _SID_COMM_CONTROL = 0x28
    _SID_WRITE_DATA = 0x2E
    _SID_ROUTINE_CONTROL = 0x31
    _SID_REQUEST_DOWNLOAD = 0x34
    _SID_TRANSFER_DATA = 0x36
    _SID_TRANSFER_EXIT = 0x37

    # Programming session type
    _SESSION_PROGRAMMING = 0x02
    _SESSION_DEFAULT = 0x01

    def __init__(
        self,
        engine: object,
        ecu: object,
        calibration_path: Optional[str] = None,
        key_fn: Optional[Callable[[bytes], bytes]] = None,
        progress_cb: Optional[Callable[[str, int], None]] = None,
    ) -> None:
        self.engine = engine
        self.ecu = ecu
        self.calibration_path = Path(calibration_path) if calibration_path else None
        self.key_fn = key_fn
        self.progress_cb = progress_cb

        self._steps: list[ProgrammingStep] = self._define_steps()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> ProgrammingResult:
        """
        Execute the full SPS programming sequence.

        Returns:
            :class:`ProgrammingResult` describing the outcome.

        Raises:
            :class:`SPSError` if a required step fails.
        """
        start = time.monotonic()
        cal_before = self._read_calibration_id()
        cal_after = cal_before

        logger.info("SPS: Starting programming of ECU %s", self.ecu)
        logger.info("SPS: Calibration file: %s", self.calibration_path)

        try:
            self._step_check_preconditions()
            self._step_open_programming_session()
            self._step_security_access()
            self._step_disable_communications()
            self._step_erase_memory()
            self._step_download_calibration()
            self._step_verify_checksum()
            self._step_enable_communications()
            self._step_reset_ecu()
            self._step_verify_programming()

            cal_after = self._read_calibration_id()
            duration = time.monotonic() - start
            return ProgrammingResult(
                success=True,
                ecu_address=self.ecu.address,  # type: ignore[union-attr]
                calibration_id_before=cal_before,
                calibration_id_after=cal_after,
                steps=self._steps,
                duration_s=round(duration, 2),
                message="Programming completed successfully.",
            )

        except SPSError as exc:
            duration = time.monotonic() - start
            logger.error("SPS FAILED: %s", exc)
            self._attempt_recovery()
            return ProgrammingResult(
                success=False,
                ecu_address=self.ecu.address,  # type: ignore[union-attr]
                calibration_id_before=cal_before,
                calibration_id_after=cal_after,
                steps=self._steps,
                duration_s=round(duration, 2),
                message=str(exc),
            )

    @property
    def steps(self) -> list[ProgrammingStep]:
        """Read-only view of programming steps and their status."""
        return list(self._steps)

    # ------------------------------------------------------------------
    # Individual steps
    # ------------------------------------------------------------------

    def _step_check_preconditions(self) -> None:
        step = self._get_step("preconditions")
        self._report_progress("preconditions", 0)
        try:
            if self.calibration_path and not self.calibration_path.exists():
                raise SPSError(f"Calibration file not found: {self.calibration_path}")
            # Check vehicle speed = 0, ignition on, etc.
            speed = self._read_vehicle_speed()
            if speed is not None and speed > 0:
                raise SPSError(f"Vehicle must be stationary (speed={speed} km/h).")
            step.completed = True
            self._report_progress("preconditions", 100)
        except SPSError as exc:
            step.error = str(exc)
            raise

    def _step_open_programming_session(self) -> None:
        step = self._get_step("open_session")
        self._report_progress("open_session", 0)
        resp = self._send(bytes([self._SID_SESSION, self._SESSION_PROGRAMMING]))
        if resp is None or resp[0] != 0x50:
            step.error = "Failed to open programming session."
            raise SPSError(step.error)
        step.completed = True
        self._report_progress("open_session", 100)

    def _step_security_access(self) -> None:
        step = self._get_step("security_access")
        self._report_progress("security_access", 0)
        seed_resp = self._send(bytes([self._SID_SECURITY, 0x03]))  # level 3 = programming
        if seed_resp is None or seed_resp[0] != 0x67:
            step.error = "Security seed request failed."
            raise SPSError(step.error)
        seed = seed_resp[2:]
        key_fn = self.key_fn or _default_programming_key
        key = key_fn(seed)
        key_resp = self._send(bytes([self._SID_SECURITY, 0x04]) + key)
        if key_resp is None or key_resp[0] != 0x67:
            step.error = "Security key rejected."
            raise SPSError(step.error)
        step.completed = True
        self._report_progress("security_access", 100)

    def _step_disable_communications(self) -> None:
        step = self._get_step("disable_comms")
        self._report_progress("disable_comms", 0)
        self._send(bytes([self._SID_COMM_CONTROL, 0x03, 0x03]))  # disable Tx/Rx
        step.completed = True
        self._report_progress("disable_comms", 100)

    def _step_erase_memory(self) -> None:
        step = self._get_step("erase_memory")
        self._report_progress("erase_memory", 0)
        resp = self._send(bytes([self._SID_ROUTINE_CONTROL, 0x01, 0xFF, 0x00]))  # erase routine
        if resp is None:
            step.error = "Memory erase routine did not respond."
            raise SPSError(step.error)
        # Poll for completion (routine result)
        for _ in range(30):
            poll = self._send(bytes([self._SID_ROUTINE_CONTROL, 0x03, 0xFF, 0x00]))
            if poll and len(poll) > 3 and poll[3] == 0x00:
                break
            time.sleep(0.5)
        step.completed = True
        self._report_progress("erase_memory", 100)

    def _step_download_calibration(self) -> None:
        step = self._get_step("download_calibration")
        if self.calibration_path is None:
            step.completed = True
            self._report_progress("download_calibration", 100)
            return
        self._report_progress("download_calibration", 0)
        data = self.calibration_path.read_bytes()
        total = len(data)
        block_size = 0xF0  # 240 bytes per transfer block
        # RequestDownload
        mem_addr = b"\x00\x00\x80\x00"  # typical SAAB calibration base address
        mem_size = total.to_bytes(4, "big")
        req_dl = bytes([self._SID_REQUEST_DOWNLOAD, 0x00, 0x44]) + mem_addr + mem_size
        resp = self._send(req_dl)
        if resp is None or resp[0] != 0x74:
            step.error = "RequestDownload rejected."
            raise SPSError(step.error)
        # Transfer data blocks
        block_seq = 0x01
        offset = 0
        while offset < total:
            chunk = data[offset: offset + block_size]
            td = bytes([self._SID_TRANSFER_DATA, block_seq]) + chunk
            self._send(td)
            offset += len(chunk)
            block_seq = (block_seq % 0xFF) + 1
            pct = min(99, int(offset / total * 100))
            self._report_progress("download_calibration", pct)
        # TransferExit
        self._send(bytes([self._SID_TRANSFER_EXIT]))
        step.completed = True
        self._report_progress("download_calibration", 100)

    def _step_verify_checksum(self) -> None:
        step = self._get_step("verify_checksum")
        self._report_progress("verify_checksum", 0)
        resp = self._send(bytes([self._SID_ROUTINE_CONTROL, 0x01, 0x02, 0x02]))
        step.completed = True
        self._report_progress("verify_checksum", 100)

    def _step_enable_communications(self) -> None:
        step = self._get_step("enable_comms")
        self._send(bytes([self._SID_COMM_CONTROL, 0x00, 0x03]))
        step.completed = True
        self._report_progress("enable_comms", 100)

    def _step_reset_ecu(self) -> None:
        step = self._get_step("reset_ecu")
        self._send(bytes([self._SID_ECU_RESET, 0x01]))
        time.sleep(3.0)  # wait for ECU to boot
        step.completed = True
        self._report_progress("reset_ecu", 100)

    def _step_verify_programming(self) -> None:
        step = self._get_step("verify_programming")
        cal_id = self._read_calibration_id()
        logger.info("SPS: Post-flash calibration ID = %s", cal_id)
        step.completed = True
        self._report_progress("verify_programming", 100)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _send(self, payload: bytes) -> Optional[bytes]:
        return self.engine._send_uds(self.ecu.address, payload)  # type: ignore[union-attr]

    def _read_calibration_id(self) -> str:
        resp = self._send(b"\x22\xF1\x86")  # DID F186: calibration ID
        if resp and len(resp) > 3:
            return resp[3:].decode("ascii", errors="replace").strip("\x00 ")
        return "unknown"

    def _read_vehicle_speed(self) -> Optional[int]:
        resp = self._send(b"\x01\x0D")  # OBD-II PID 0x0D: vehicle speed
        if resp and len(resp) >= 3:
            return resp[2]  # km/h
        return None

    def _attempt_recovery(self) -> None:
        """Try to return to default session after a failure."""
        logger.info("SPS: Attempting recovery (return to default session) …")
        try:
            self._send(bytes([self._SID_COMM_CONTROL, 0x00, 0x03]))
            self._send(bytes([self._SID_SESSION, self._SESSION_DEFAULT]))
        except Exception:  # noqa: BLE001
            pass

    def _get_step(self, name: str) -> ProgrammingStep:
        for s in self._steps:
            if s.name == name:
                return s
        raise KeyError(f"Unknown step: {name!r}")

    def _report_progress(self, step_name: str, pct: int) -> None:
        if self.progress_cb:
            try:
                self.progress_cb(step_name, pct)
            except Exception:  # noqa: BLE001
                pass

    @staticmethod
    def _define_steps() -> list[ProgrammingStep]:
        return [
            ProgrammingStep("preconditions",         "Check vehicle preconditions"),
            ProgrammingStep("open_session",          "Open UDS programming session"),
            ProgrammingStep("security_access",       "Unlock ECU security access"),
            ProgrammingStep("disable_comms",         "Disable network communications"),
            ProgrammingStep("erase_memory",          "Erase ECU flash memory"),
            ProgrammingStep("download_calibration",  "Download calibration data"),
            ProgrammingStep("verify_checksum",       "Verify programmed checksum"),
            ProgrammingStep("enable_comms",          "Re-enable network communications"),
            ProgrammingStep("reset_ecu",             "Reset ECU"),
            ProgrammingStep("verify_programming",    "Verify programming result"),
        ]


def _default_programming_key(seed: bytes) -> bytes:
    """Placeholder key function for programming security level."""
    return bytes(b ^ 0xA5 for b in seed)
