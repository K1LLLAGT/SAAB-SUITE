"""
Core diagnostic engine for SAAB/GM vehicles.

Handles connection lifecycle, ECU discovery, and orchestration of
diagnostic sessions across the vehicle network.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ECU information
# ---------------------------------------------------------------------------

@dataclass
class ECUInfo:
    """Metadata about a discovered ECU."""
    address: int
    name: str
    software_version: str = "unknown"
    hardware_version: str = "unknown"
    vin: str = ""

    def __str__(self) -> str:
        return f"ECU[0x{self.address:02X}] {self.name} SW={self.software_version}"


# ---------------------------------------------------------------------------
# Diagnostic engine
# ---------------------------------------------------------------------------

class DiagnosticEngine:
    """
    Central orchestration engine for SAAB/GM diagnostics.

    Manages the connection to a vehicle interface (J2534 or python-can bus),
    discovers ECUs on the network, and provides high-level methods for reading
    DTCs, live data, and performing bi-directional tests.

    Example usage::

        engine = DiagnosticEngine(interface="j2534", protocol="ISO15765")
        engine.connect()
        ecus = engine.discover_ecus()
        dtcs = engine.read_dtcs(ecus[0])
        engine.disconnect()
    """

    # Known SAAB/GM ECU addresses (subset)
    KNOWN_ECUS: dict[int, str] = {
        0x7E0: "ECM (Engine Control Module)",
        0x7E1: "TCM (Transmission Control Module)",
        0x7E2: "ABS/TCS Module",
        0x7E3: "BCM (Body Control Module)",
        0x7E4: "HVAC Module",
        0x7E5: "SRS (Airbag) Module",
        0x7E6: "Instrument Cluster",
        0x7E7: "Fuel Pump Control Module",
        0x7E8: "TPMS Module",
        0x7E9: "Suspension Control Module",
        0x720: "Tech2/GDS2 Pass-Through",
    }

    def __init__(
        self,
        interface: str = "j2534",
        protocol: str = "ISO15765",
        baudrate: int = 500000,
        channel: int = 1,
    ) -> None:
        """
        Args:
            interface: Interface type – ``"j2534"`` (hardware pass-through) or
                       ``"socketcan"`` / ``"kvaser"`` / ``"peak"`` (python-can).
            protocol:  Diagnostic protocol – ``"ISO15765"`` (UDS/CAN) or
                       ``"KWP2000"`` (K-line).
            baudrate:  CAN bus baudrate in bits/s.
            channel:   Physical channel index on the interface hardware.
        """
        self.interface = interface
        self.protocol = protocol
        self.baudrate = baudrate
        self.channel = channel

        self._connected: bool = False
        self._ecus: list[ECUInfo] = []
        self._bus: Optional[object] = None  # python-can Bus or J2534Channel

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open a connection to the vehicle interface."""
        if self._connected:
            logger.warning("Engine already connected.")
            return
        logger.info(
            "Connecting via %s / %s @ %d bps (channel %d)",
            self.interface,
            self.protocol,
            self.baudrate,
            self.channel,
        )
        self._bus = self._open_bus()
        self._connected = True
        logger.info("Connection established.")

    def disconnect(self) -> None:
        """Close the connection to the vehicle interface."""
        if not self._connected:
            return
        if self._bus is not None:
            try:
                self._bus.shutdown()  # type: ignore[union-attr]
            except Exception:  # noqa: BLE001
                pass
        self._connected = False
        self._bus = None
        logger.info("Disconnected from vehicle interface.")

    def __enter__(self) -> "DiagnosticEngine":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.disconnect()

    # ------------------------------------------------------------------
    # ECU discovery
    # ------------------------------------------------------------------

    def discover_ecus(self, timeout: float = 5.0) -> list[ECUInfo]:
        """
        Broadcast a UDS TesterPresent and collect responding ECU addresses.

        Args:
            timeout: Seconds to wait for responses.

        Returns:
            List of :class:`ECUInfo` objects for each responding ECU.
        """
        self._require_connected()
        logger.info("Starting ECU discovery (timeout=%.1fs) …", timeout)
        discovered: list[ECUInfo] = []

        for address, name in self.KNOWN_ECUS.items():
            response = self._send_uds(address, b"\x3E\x00")  # TesterPresent
            if response is not None:
                ecu = ECUInfo(address=address, name=name)
                self._populate_ecu_info(ecu)
                discovered.append(ecu)
                logger.debug("Found: %s", ecu)

        self._ecus = discovered
        logger.info("Discovery complete – %d ECU(s) found.", len(discovered))
        return discovered

    # ------------------------------------------------------------------
    # DTC operations
    # ------------------------------------------------------------------

    def read_dtcs(self, ecu: ECUInfo) -> list["DTCCode"]:
        """Read stored Diagnostic Trouble Codes from *ecu*."""
        from .diagnostic import DTCCode  # local import to avoid circular
        self._require_connected()
        logger.info("Reading DTCs from %s …", ecu)
        raw = self._send_uds(ecu.address, b"\x19\x02\xFF")  # ReadDTCInfo
        if raw is None:
            return []
        return DTCCode.parse_uds_response(raw)

    def clear_dtcs(self, ecu: ECUInfo) -> bool:
        """Clear all stored DTCs on *ecu*.  Returns True on success."""
        self._require_connected()
        logger.info("Clearing DTCs on %s …", ecu)
        response = self._send_uds(ecu.address, b"\x14\xFF\xFF\xFF")  # ClearDTC
        return response is not None

    # ------------------------------------------------------------------
    # Live data (PIDs)
    # ------------------------------------------------------------------

    def read_pid(self, ecu: ECUInfo, pid: int) -> Optional[bytes]:
        """
        Read a single OBD-II / UDS data identifier from *ecu*.

        Args:
            ecu: Target ECU.
            pid: Service $01 PID or UDS DID (0x0000–0xFFFF).

        Returns:
            Raw response bytes, or None if no response.
        """
        self._require_connected()
        if pid <= 0xFF:
            payload = bytes([0x01, pid])  # OBD-II Mode 01
        else:
            payload = bytes([0x22, (pid >> 8) & 0xFF, pid & 0xFF])  # UDS ReadDataByID
        return self._send_uds(ecu.address, payload)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _open_bus(self) -> object:
        """Instantiate the appropriate bus object."""
        if self.interface.lower() == "j2534":
            try:
                from j2534.interface import J2534Interface  # absolute import
            except ImportError:
                from ..j2534.interface import J2534Interface  # relative import fallback
            bus = J2534Interface(protocol=self.protocol, baudrate=self.baudrate, channel=self.channel)
            bus.open()
            return bus
        # Fall back to python-can
        try:
            import importlib
            python_can = importlib.import_module("can")
            if not hasattr(python_can, "Bus"):
                raise ImportError("python-can Bus not found (local 'can' module may have shadowed it)")
            return python_can.Bus(interface=self.interface, bitrate=self.baudrate, channel=self.channel)
        except (ImportError, Exception):  # noqa: BLE001
            logger.warning("python-can not available; using null bus.")
            return _NullBus()

    def _send_uds(self, address: int, payload: bytes, timeout: float = 1.0) -> Optional[bytes]:
        """Send a UDS request and return the response payload."""
        if self._bus is None:
            return None
        try:
            return self._bus.send_uds(address, payload, timeout=timeout)  # type: ignore[union-attr]
        except AttributeError:
            # python-can Bus does not have send_uds – use raw CAN frame
            return self._send_raw_can(address, payload, timeout)
        except Exception as exc:  # noqa: BLE001
            logger.debug("UDS error on 0x%03X: %s", address, exc)
            return None

    def _send_raw_can(self, address: int, payload: bytes, timeout: float) -> Optional[bytes]:
        """Thin wrapper to send ISO 15765-2 single frames via python-can."""
        try:
            import importlib
            python_can = importlib.import_module("can")
            if not hasattr(python_can, "Message"):
                return None
            # Single frame: length nibble + data
            data = bytes([len(payload)]) + payload
            msg = python_can.Message(arbitration_id=address, data=data, is_extended_id=False)
            self._bus.send(msg)  # type: ignore[union-attr]
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                reply = self._bus.recv(timeout=0.1)  # type: ignore[union-attr]
                if reply and reply.arbitration_id == (address + 8):
                    return bytes(reply.data)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Raw CAN error: %s", exc)
        return None

    def _populate_ecu_info(self, ecu: ECUInfo) -> None:
        """Query software/hardware version and VIN from an ECU."""
        sw = self._send_uds(ecu.address, b"\x22\xF1\x89")  # SW version DID
        if sw and len(sw) > 3:
            ecu.software_version = sw[3:].decode("ascii", errors="replace").strip()

        hw = self._send_uds(ecu.address, b"\x22\xF1\x91")  # HW version DID
        if hw and len(hw) > 3:
            ecu.hardware_version = hw[3:].decode("ascii", errors="replace").strip()

        vin_raw = self._send_uds(ecu.address, b"\x22\xF1\x90")  # VIN DID
        if vin_raw and len(vin_raw) > 3:
            ecu.vin = vin_raw[3:20].decode("ascii", errors="replace").strip()

    def _require_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("DiagnosticEngine is not connected. Call connect() first.")


# ---------------------------------------------------------------------------
# Null bus – used when no real interface is available
# ---------------------------------------------------------------------------

class _NullBus:
    """A no-op bus that always returns None (for unit-testing without hardware)."""

    def send_uds(self, address: int, payload: bytes, timeout: float = 1.0) -> None:  # noqa: ARG002
        return None

    def shutdown(self) -> None:
        pass
