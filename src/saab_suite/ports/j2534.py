"""J2534 device port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from saab_suite.domain.can.frame import CanFrame


class IJ2534Device(Protocol):
    """Define the vendor-neutral J2534 device interface."""

    def connect(self, protocol: int, flags: int, baudrate: int) -> int:
        """Open a J2534 channel and return its identifier."""
        ...

    def disconnect(self, channel_id: int) -> None:
        """Close a previously opened J2534 channel."""
        ...

    def read_msgs(self, channel_id: int, max_msgs: int, timeout_ms: int) -> list[CanFrame]:
        """Read CAN frames from a J2534 channel."""
        ...

    def write_msgs(self, channel_id: int, frames: list[CanFrame], timeout_ms: int) -> int:
        """Write CAN frames to a J2534 channel."""
        ...

    def start_msg_filter(
        self,
        channel_id: int,
        filter_type: int,
        mask: bytes,
        pattern: bytes,
        flow_control: bytes | None = None,
    ) -> int:
        """Create a message filter on a J2534 channel."""
        ...

    def ioctl(self, channel_id: int, ioctl_id: int, input_arg: Any, output_arg: Any) -> None:
        """Run an IOCTL operation on a J2534 channel."""
        ...
