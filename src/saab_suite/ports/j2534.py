"""IJ2534Device -- abstract J2534 PassThru device."""

from __future__ import annotations

from typing import Any, Protocol

from saab_suite.domain.can.frame import CanFrame


class IJ2534Device(Protocol):
    """Vendor-neutral interface to a J2534 device."""

    def connect(self, protocol: int, flags: int, baudrate: int) -> int: ...
    def disconnect(self, channel_id: int) -> None: ...
    def read_msgs(self, channel_id: int, max_msgs: int, timeout_ms: int) -> list[CanFrame]: ...
    def write_msgs(self, channel_id: int, frames: list[CanFrame], timeout_ms: int) -> int: ...
    def start_msg_filter(
        self,
        channel_id: int,
        filter_type: int,
        mask: bytes,
        pattern: bytes,
        flow_control: bytes | None = None,
    ) -> int: ...
    def ioctl(self, channel_id: int, ioctl_id: int, input_arg: Any, output_arg: Any) -> None: ...
