from __future__ import annotations

from dataclasses import dataclass

from saab_suite.runtime.can_config import load_can_config

try:
    import can
except ImportError:
    can = None


@dataclass
class CanFrame:
    """Represent can frame."""
    can_id: int
    data: bytes


class CanInterface:
    """Unified CAN interface abstraction backed by python-can."""

    def __init__(self, channel: str | None = None, bustype: str | None = None):
        cfg = load_can_config()
        self._channel = channel or cfg.channel
        self._bustype = bustype or cfg.bustype
        self._bitrate = cfg.bitrate
        self._bus: can.Bus | None = None

    def open(self) -> None:
        """Open the resource."""
        if can is None:
            raise RuntimeError("python-can is not installed. Install saab[hardware].")

        kwargs = {"channel": self._channel, "bustype": self._bustype}
        if self._bitrate is not None:
            kwargs["bitrate"] = self._bitrate

        self._bus = can.interface.Bus(**kwargs)

    def close(self) -> None:
        """Close the resource."""
        if self._bus is not None:
            self._bus.shutdown()
            self._bus = None

    def send(self, frame: CanFrame) -> None:
        """Send the requested payload."""
        if self._bus is None:
            raise RuntimeError("CAN interface not open")
        msg = can.Message(
            arbitration_id=frame.can_id,
            data=frame.data,
            is_extended_id=True,
        )
        self._bus.send(msg)

    def recv(self, timeout: float = 0.1) -> CanFrame | None:
        """Receive the next payload."""
        if self._bus is None:
            raise RuntimeError("CAN interface not open")
        msg = self._bus.recv(timeout)
        if msg is None:
            return None
        return CanFrame(can_id=msg.arbitration_id, data=bytes(msg.data))
