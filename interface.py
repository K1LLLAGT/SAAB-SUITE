from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from saab_suite.runtime.can_config import load_can_config

try:
    import can
except ImportError:
    can = None

# Largest 11-bit (standard) CAN identifier. Anything above this must be extended.
_STD_ID_MAX = 0x7FF


@dataclass
class CanFrame:
    """A CAN frame.

    Args:
        can_id: 11-bit standard or 29-bit extended identifier.
        data: 0..8 payload bytes.
        is_extended_id: True/False to force the frame format, or None (default)
            to auto-detect: standard for can_id <= 0x7FF, extended otherwise.
            Auto-detect keeps 11-bit OBD addressing (0x7E0/0x7E8) standard while
            letting 29-bit GMLAN enhanced IDs (0x18DAxxxx) go out extended.
    """

    can_id: int
    data: bytes
    is_extended_id: Optional[bool] = None

    def __post_init__(self) -> None:
        if len(self.data) > 8:
            raise ValueError("CAN 2.0 frame data must be <= 8 bytes")

    @property
    def extended(self) -> bool:
        """Resolved frame format: explicit flag if set, else inferred from id width."""
        if self.is_extended_id is not None:
            return self.is_extended_id
        return self.can_id > _STD_ID_MAX


class CanInterface:
    """Unified CAN interface abstraction backed by python-can."""

    def __init__(self, channel: str | None = None, bustype: str | None = None):
        cfg = load_can_config()
        self._channel = channel or cfg.channel
        self._bustype = bustype or cfg.bustype
        self._bitrate = cfg.bitrate
        self._bus: Optional["can.Bus"] = None

    def open(self) -> None:
        if can is None:
            raise RuntimeError("python-can is not installed. Install saab_suite[hardware].")

        # python-can 4.x prefers `interface=`; `bustype=` is still accepted as an alias.
        kwargs = {"channel": self._channel, "interface": self._bustype}
        if self._bitrate is not None:
            kwargs["bitrate"] = self._bitrate

        self._bus = can.Bus(**kwargs)

    def close(self) -> None:
        if self._bus is not None:
            self._bus.shutdown()
            self._bus = None

    def send(self, frame: CanFrame) -> None:
        if self._bus is None:
            raise RuntimeError("CAN interface not open")
        msg = can.Message(
            arbitration_id=frame.can_id,
            data=frame.data,
            is_extended_id=frame.extended,
        )
        self._bus.send(msg)

    def recv(self, timeout: float = 0.1) -> Optional[CanFrame]:
        if self._bus is None:
            raise RuntimeError("CAN interface not open")
        msg = self._bus.recv(timeout)
        if msg is None:
            return None
        return CanFrame(
            can_id=msg.arbitration_id,
            data=bytes(msg.data),
            is_extended_id=msg.is_extended_id,
        )
