"""
SAE J2534 pass-through API wrapper.

Provides a Python interface to J2534 DLL/SO pass-through devices (e.g.
GM MDI, Bosch KTS, Drew Technologies MongoosePro, etc.) through ctypes.

The J2534 API (SAE J2534-1 and -2) standardises how diagnostic software
talks to in-vehicle networks.  This module wraps the Windows DLL API with
a clean Python façade that falls back gracefully when the DLL is absent
(e.g. on Linux developer machines).

References:
  SAE J2534-1:2015 – Pass-Thru Programming Interface
  SAE J2534-2:2019 – Pass-Thru Programming Interface (extended protocols)
"""
from __future__ import annotations

import ctypes
import logging
import platform
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class J2534Error(Exception):
    """Raised when a J2534 API call returns a non-zero status code."""

    STATUS_CODES: dict[int, str] = {
        0x00: "STATUS_NOERROR",
        0x01: "ERR_NOT_SUPPORTED",
        0x02: "ERR_INVALID_CHANNEL_ID",
        0x03: "ERR_INVALID_PROTOCOL_ID",
        0x04: "ERR_NULL_PARAMETER",
        0x05: "ERR_INVALID_IOCTL_VALUE",
        0x06: "ERR_INVALID_FLAGS",
        0x07: "ERR_FAILED",
        0x08: "ERR_DEVICE_NOT_CONNECTED",
        0x09: "ERR_TIMEOUT",
        0x0A: "ERR_INVALID_MSG",
        0x0B: "ERR_INVALID_TIME_INTERVAL",
        0x0C: "ERR_EXCEEDED_LIMIT",
        0x0D: "ERR_INVALID_MSG_ID",
        0x0E: "ERR_DEVICE_IN_USE",
        0x0F: "ERR_INVALID_IOCTL_ID",
        0x10: "ERR_BUFFER_EMPTY",
        0x11: "ERR_BUFFER_FULL",
        0x12: "ERR_BUFFER_OVERFLOW",
        0x13: "ERR_PIN_INVALID",
        0x14: "ERR_CHANNEL_IN_USE",
        0x15: "ERR_MSG_PROTOCOL_ID",
        0x16: "ERR_INVALID_FILTER_ID",
        0x17: "ERR_NO_FLOW_CONTROL",
        0x18: "ERR_NOT_UNIQUE",
        0x19: "ERR_INVALID_BAUDRATE",
        0x1A: "ERR_INVALID_DEVICE_ID",
    }

    def __init__(self, status: int, context: str = "") -> None:
        self.status = status
        name = self.STATUS_CODES.get(status, f"UNKNOWN_ERROR(0x{status:02X})")
        msg = f"J2534 error: {name} (0x{status:02X})"
        if context:
            msg += f" [{context}]"
        super().__init__(msg)


# ---------------------------------------------------------------------------
# J2534 protocol IDs
# ---------------------------------------------------------------------------

class Protocol(int):
    J1850VPW = 0x01
    J1850PWM = 0x02
    ISO9141 = 0x03
    ISO14230 = 0x04
    CAN = 0x05
    ISO15765 = 0x06
    SCI_A_ENGINE = 0x07
    SCI_A_TRANS = 0x08
    SCI_B_ENGINE = 0x09
    SCI_B_TRANS = 0x0A


PROTOCOL_NAMES: dict[int, str] = {
    Protocol.J1850VPW: "J1850VPW",
    Protocol.J1850PWM: "J1850PWM",
    Protocol.ISO9141: "ISO9141",
    Protocol.ISO14230: "ISO14230/KWP2000",
    Protocol.CAN: "CAN",
    Protocol.ISO15765: "ISO15765/UDS",
}


# ---------------------------------------------------------------------------
# Pass-through channel
# ---------------------------------------------------------------------------

@dataclass
class PassThruChannel:
    """
    Represents an open J2534 pass-through channel.

    Do not instantiate directly – use :meth:`J2534Interface.connect_to_channel`.
    """

    channel_id: int
    protocol_id: int
    baudrate: int
    _iface: "J2534Interface"

    def send_uds(self, address: int, payload: bytes, timeout: int = 1000) -> Optional[bytes]:
        """
        Send a UDS request and wait for the response.

        Args:
            address: Target ECU CAN ID.
            payload: UDS request payload (without CAN-TP framing).
            timeout: Response timeout in milliseconds.

        Returns:
            UDS response payload bytes, or None if no response.
        """
        return self._iface._send_uds_on_channel(self.channel_id, address, payload, timeout)

    def close(self) -> None:
        """Disconnect this channel."""
        self._iface._disconnect_channel(self.channel_id)

    def __enter__(self) -> "PassThruChannel":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# J2534 interface
# ---------------------------------------------------------------------------

class J2534Interface:
    """
    Python wrapper around a J2534 pass-through DLL.

    On Windows, the DLL path is read from the registry (HKLM\\SOFTWARE\\
    PassThruSupport.04.04\\<device>) or can be supplied explicitly.
    On non-Windows platforms, the class operates in *simulation mode*
    (all calls succeed but return no data) to allow development without
    physical hardware.

    Args:
        dll_path: Explicit path to the J2534 DLL.  Auto-detected if None.
        protocol: Default protocol for new channels (``"ISO15765"`` etc.).
        baudrate: Default channel baudrate.
        channel:  Channel index (1-based, used when opened via engine.core).
    """

    def __init__(
        self,
        dll_path: Optional[str] = None,
        protocol: str = "ISO15765",
        baudrate: int = 500_000,
        channel: int = 1,
    ) -> None:
        self.dll_path = dll_path
        self.protocol_name = protocol
        self.baudrate = baudrate
        self.channel = channel

        self._dll: Optional[ctypes.CDLL] = None
        self._device_id: int = 0
        self._simulation_mode = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def open(self) -> None:
        """Open the J2534 device."""
        if platform.system() != "Windows":
            logger.info("Non-Windows platform detected; entering J2534 simulation mode.")
            self._simulation_mode = True
            return
        dll_path = self.dll_path or self._find_dll()
        if dll_path is None:
            logger.warning("No J2534 DLL found; entering simulation mode.")
            self._simulation_mode = True
            return
        try:
            self._dll = ctypes.WinDLL(dll_path)  # type: ignore[attr-defined]
            device_id = ctypes.c_ulong(0)
            self._check(self._dll.PassThruOpen(None, ctypes.byref(device_id)), "PassThruOpen")
            self._device_id = device_id.value
            logger.info("J2534 device opened (ID=%d, DLL=%s)", self._device_id, dll_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("J2534 DLL load failed: %s.  Entering simulation mode.", exc)
            self._simulation_mode = True

    def close(self) -> None:
        """Close the J2534 device."""
        if self._simulation_mode or self._dll is None:
            return
        try:
            self._check(self._dll.PassThruClose(self._device_id), "PassThruClose")
        except Exception:  # noqa: BLE001
            pass
        self._dll = None
        logger.info("J2534 device closed.")

    def shutdown(self) -> None:
        """Alias for :meth:`close` (python-can bus compatibility)."""
        self.close()

    def __enter__(self) -> "J2534Interface":
        self.open()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Channel management
    # ------------------------------------------------------------------

    def connect_to_channel(
        self,
        protocol: Optional[str] = None,
        baudrate: Optional[int] = None,
        flags: int = 0,
    ) -> PassThruChannel:
        """
        Open a protocol channel on the device.

        Args:
            protocol: Override the default protocol.
            baudrate: Override the default baudrate.
            flags:    J2534 connect flags (CAN_29BIT_ID etc.).

        Returns:
            A :class:`PassThruChannel` ready for use.
        """
        proto_name = protocol or self.protocol_name
        proto_id = self._protocol_id(proto_name)
        baud = baudrate or self.baudrate

        if self._simulation_mode or self._dll is None:
            logger.debug("J2534 sim: connecting channel proto=%s baud=%d", proto_name, baud)
            return PassThruChannel(channel_id=1, protocol_id=proto_id, baudrate=baud, _iface=self)

        channel_id = ctypes.c_ulong(0)
        self._check(
            self._dll.PassThruConnect(
                self._device_id, proto_id, flags, baud, ctypes.byref(channel_id)
            ),
            "PassThruConnect",
        )
        return PassThruChannel(channel_id=channel_id.value, protocol_id=proto_id, baudrate=baud, _iface=self)

    # ------------------------------------------------------------------
    # Engine.core compatibility shim
    # ------------------------------------------------------------------

    def send_uds(self, address: int, payload: bytes, timeout: float = 1.0) -> Optional[bytes]:
        """Direct UDS send (used by DiagnosticEngine)."""
        return self._send_uds_on_channel(self.channel, address, payload, int(timeout * 1000))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _send_uds_on_channel(
        self, channel_id: int, address: int, payload: bytes, timeout_ms: int
    ) -> Optional[bytes]:
        if self._simulation_mode:
            # Return a positive response echo (SID | 0x40) for testing
            if payload:
                return bytes([payload[0] | 0x40]) + payload[1:]
            return None

        if self._dll is None:
            return None

        # Build a minimal PASSTHRU_MSG structure
        # This is a simplified implementation – a production version would
        # handle flow control, multi-frame assembly, etc.
        try:
            msg_data = self._build_isotp_frame(address, payload)
            # Simplified: use ctypes structures for PASSTHRU_MSG
            # (Full implementation would use proper ctypes Structure definitions)
            logger.debug("J2534: sending %d bytes to 0x%03X", len(payload), address)
            return None  # Placeholder – full implementation pending
        except Exception as exc:  # noqa: BLE001
            logger.warning("J2534 send error: %s", exc)
            return None

    def _disconnect_channel(self, channel_id: int) -> None:
        if self._simulation_mode or self._dll is None:
            return
        try:
            self._dll.PassThruDisconnect(channel_id)
        except Exception:  # noqa: BLE001
            pass

    @staticmethod
    def _build_isotp_frame(address: int, payload: bytes) -> bytes:
        """Build a minimal ISO 15765-2 single-frame CAN message."""
        if len(payload) > 7:
            raise ValueError("Multi-frame not implemented in this helper.")
        return struct.pack(">I", address) + bytes([len(payload)]) + payload

    @staticmethod
    def _protocol_id(name: str) -> int:
        mapping = {
            "J1850VPW": Protocol.J1850VPW,
            "J1850PWM": Protocol.J1850PWM,
            "ISO9141": Protocol.ISO9141,
            "ISO14230": Protocol.ISO14230,
            "KWP2000": Protocol.ISO14230,
            "CAN": Protocol.CAN,
            "ISO15765": Protocol.ISO15765,
            "UDS": Protocol.ISO15765,
        }
        pid = mapping.get(name.upper())
        if pid is None:
            raise ValueError(f"Unknown J2534 protocol: {name!r}")
        return pid

    @staticmethod
    def _check(status: int, context: str) -> None:
        if status != 0:
            raise J2534Error(status, context)

    @staticmethod
    def _find_dll() -> Optional[str]:
        """Enumerate installed J2534 DLLs from the Windows registry."""
        try:
            import winreg  # type: ignore
            base = r"SOFTWARE\PassThruSupport.04.04"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as root:
                for i in range(winreg.QueryInfoKey(root)[0]):
                    sub_name = winreg.EnumKey(root, i)
                    with winreg.OpenKey(root, sub_name) as sub:
                        try:
                            dll, _ = winreg.QueryValueEx(sub, "FunctionLibrary")
                            if Path(dll).exists():
                                logger.info("Found J2534 DLL: %s (%s)", dll, sub_name)
                                return dll
                        except FileNotFoundError:
                            continue
        except Exception:  # noqa: BLE001
            pass
        return None
