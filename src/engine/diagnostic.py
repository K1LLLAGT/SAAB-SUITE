"""
Diagnostic session and DTC code definitions for SAAB/GM vehicles.

Covers UDS (ISO 14229), OBD-II (SAE J1979), and GM-proprietary fault
classifications used across the SAAB 9-3, 9-5, and related GM platforms.
"""
from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import ClassVar, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTC severity / status masks (ISO 14229-1 §11.3.2)
# ---------------------------------------------------------------------------

class DTCSeverity(enum.IntEnum):
    MAINTENANCE_ONLY = 0x20
    CHECK_AT_NEXT_HALT = 0x40
    CHECK_IMMEDIATELY = 0x60


class DTCStatusMask(enum.IntFlag):
    TEST_FAILED = 0x01
    TEST_FAILED_THIS_OPERATION_CYCLE = 0x02
    PENDING = 0x04
    CONFIRMED = 0x08
    TEST_NOT_COMPLETED_SINCE_LAST_CLEAR = 0x10
    TEST_FAILED_SINCE_LAST_CLEAR = 0x20
    TEST_NOT_COMPLETED_THIS_OPERATION_CYCLE = 0x40
    WARNING_INDICATOR_REQUESTED = 0x80


# ---------------------------------------------------------------------------
# DTC code
# ---------------------------------------------------------------------------

@dataclass
class DTCCode:
    """A single Diagnostic Trouble Code with status information."""

    raw_code: int
    status: int = 0

    # Human-readable descriptions for common SAAB/GM codes (subset)
    _DESCRIPTIONS: ClassVar[dict[int, str]] = {}

    # Class-level registry of known codes
    _KNOWN_CODES: ClassVar[dict[int, str]] = {
        0x0100: "Mass Air Flow / Volume Air Flow Circuit",
        0x0101: "Mass Air Flow Circuit Range/Performance",
        0x0300: "Random/Multiple Cylinder Misfire Detected",
        0x0420: "Catalyst System Efficiency Below Threshold (Bank 1)",
        0x0440: "Evaporative Emission Control System Malfunction",
        0x0500: "Vehicle Speed Sensor",
        0x0601: "PCM – Internal Control Module Memory Check Sum Error",
        0x0605: "PCM – Internal Control Module EEPROM Error",
        # GM proprietary range
        0x1000: "GM: ECM Power Supply",
        0x1600: "GM: Lost Communication With ECM/PCM",
    }

    @property
    def code_str(self) -> str:
        """Return the SAE-style code string, e.g. ``P0100``."""
        category = (self.raw_code >> 14) & 0x03
        prefix = ["P", "C", "B", "U"][category]
        number = self.raw_code & 0x3FFF
        return f"{prefix}{number:04X}"

    @property
    def description(self) -> str:
        number = self.raw_code & 0x3FFF
        return self._KNOWN_CODES.get(number, "Unknown fault")

    @property
    def is_confirmed(self) -> bool:
        return bool(self.status & DTCStatusMask.CONFIRMED)

    @property
    def is_pending(self) -> bool:
        return bool(self.status & DTCStatusMask.PENDING)

    def __str__(self) -> str:
        flags = []
        if self.is_confirmed:
            flags.append("CONFIRMED")
        if self.is_pending:
            flags.append("PENDING")
        flag_str = ", ".join(flags) if flags else "STORED"
        return f"{self.code_str}: {self.description} [{flag_str}]"

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @classmethod
    def parse_uds_response(cls, data: bytes) -> list["DTCCode"]:
        """
        Parse a UDS 0x59 (ReadDTCInformation) positive response.

        Format per ISO 14229-1:
          Byte 0: 0x59 (response SID)
          Byte 1: subFunction echo
          Byte 2: DTCStatusAvailabilityMask
          Bytes 3+: groups of 4 bytes [DTC high, DTC mid, DTC low, status]
        """
        codes: list[DTCCode] = []
        if len(data) < 4:
            return codes
        if data[0] != 0x59:
            logger.warning("Expected UDS response SID 0x59, got 0x%02X", data[0])
            return codes

        idx = 3
        while idx + 3 < len(data):
            raw = (data[idx] << 16) | (data[idx + 1] << 8) | data[idx + 2]
            status = data[idx + 3]
            codes.append(cls(raw_code=raw, status=status))
            idx += 4
        return codes


# ---------------------------------------------------------------------------
# Diagnostic session
# ---------------------------------------------------------------------------

class SessionType(enum.IntEnum):
    DEFAULT = 0x01
    PROGRAMMING = 0x02
    EXTENDED_DIAGNOSTIC = 0x03
    SAFETY_SYSTEM_DIAGNOSTIC = 0x04


@dataclass
class DiagnosticSession:
    """
    Represents an active UDS diagnostic session with a single ECU.

    A session wraps the low-level UDS session-control handshake and keeps
    track of the security-access seed/key exchange state.

    Example::

        session = DiagnosticSession(engine, ecu, SessionType.EXTENDED_DIAGNOSTIC)
        session.open()
        dtcs = session.read_dtcs()
        session.close()
    """

    engine: object  # DiagnosticEngine
    ecu: object  # ECUInfo
    session_type: SessionType = SessionType.DEFAULT

    _active: bool = field(default=False, init=False, repr=False)
    _security_unlocked: bool = field(default=False, init=False, repr=False)
    _seed: Optional[bytes] = field(default=None, init=False, repr=False)

    def open(self) -> None:
        """Send DiagnosticSessionControl to open the requested session."""
        if self._active:
            logger.warning("Session already open.")
            return
        payload = bytes([0x10, int(self.session_type)])
        response = self.engine._send_uds(self.ecu.address, payload)  # type: ignore[union-attr]
        if response and response[0] == 0x50:
            self._active = True
            logger.info(
                "Opened %s session with %s", self.session_type.name, self.ecu
            )
        else:
            raise RuntimeError(
                f"Failed to open {self.session_type.name} session with {self.ecu}. "
                f"Response: {response!r}"
            )

    def close(self) -> None:
        """Return to default session."""
        if not self._active:
            return
        payload = bytes([0x10, int(SessionType.DEFAULT)])
        self.engine._send_uds(self.ecu.address, payload)  # type: ignore[union-attr]
        self._active = False
        self._security_unlocked = False
        logger.info("Closed session with %s", self.ecu)

    def unlock_security(self, level: int = 0x01, key_fn=None) -> bool:
        """
        Perform UDS Security Access (0x27) seed/key exchange.

        Args:
            level:  Security access level (odd = request seed).
            key_fn: Callable ``(seed: bytes) -> bytes`` that computes the key.
                    Defaults to a simple XOR placeholder.

        Returns:
            True if security was successfully unlocked.
        """
        if not self._active:
            raise RuntimeError("Session must be open before unlocking security.")

        seed_resp = self.engine._send_uds(  # type: ignore[union-attr]
            self.ecu.address, bytes([0x27, level])
        )
        if seed_resp is None or seed_resp[0] != 0x67:
            logger.warning("Security access seed request failed.")
            return False

        self._seed = seed_resp[2:]
        key_fn = key_fn or _default_key_fn
        key = key_fn(self._seed)
        key_resp = self.engine._send_uds(  # type: ignore[union-attr]
            self.ecu.address, bytes([0x27, level + 1]) + key
        )
        if key_resp and key_resp[0] == 0x67:
            self._security_unlocked = True
            logger.info("Security level 0x%02X unlocked on %s", level, self.ecu)
            return True
        logger.warning("Security key rejected by %s", self.ecu)
        return False

    def read_dtcs(self) -> list[DTCCode]:
        """Convenience wrapper – read DTCs through this session."""
        return self.engine.read_dtcs(self.ecu)  # type: ignore[union-attr]

    def clear_dtcs(self) -> bool:
        """Convenience wrapper – clear DTCs through this session."""
        return self.engine.clear_dtcs(self.ecu)  # type: ignore[union-attr]

    def __enter__(self) -> "DiagnosticSession":
        self.open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# Default key function (placeholder – replace with actual GM algorithm)
# ---------------------------------------------------------------------------

def _default_key_fn(seed: bytes) -> bytes:
    """
    Placeholder security-key computation.

    .. warning::
        This is NOT the real GM security algorithm.  Replace with the
        appropriate implementation for the target ECU.
    """
    return bytes(b ^ 0xFF for b in seed)
