"""J2534 PassThru DLL binding for Windows.

This is the **only** file in the entire suite that may import ``ctypes``.
Enforced by an import-linter contract in ``pyproject.toml``.

Phase-2 implementation. The class shape is fixed; the bodies are stubs.
The ctypes import is deferred to keep this file import-clean on non-Windows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from saab_suite.kernel.errors import J2534Error
from saab_suite.ports.j2534 import IJ2534Device

if TYPE_CHECKING:
    from saab_suite.domain.can.frame import CanFrame


class WindowsJ2534Device(IJ2534Device):
    """J2534 device backed by a Windows PassThru DLL."""

    def __init__(self, dll_path: str, expected_sha256: str | None = None) -> None:
        self.dll_path = dll_path
        self.expected_sha256 = expected_sha256

    def connect(self, protocol: int, flags: int, baudrate: int) -> int:
        raise J2534Error("WindowsJ2534Device not yet implemented")

    def disconnect(self, channel_id: int) -> None:
        raise J2534Error("WindowsJ2534Device not yet implemented")

    def read_msgs(self, channel_id: int, max_msgs: int, timeout_ms: int) -> list[CanFrame]:
        raise J2534Error("WindowsJ2534Device not yet implemented")

    def write_msgs(self, channel_id: int, frames: list[CanFrame], timeout_ms: int) -> int:
        raise J2534Error("WindowsJ2534Device not yet implemented")

    def start_msg_filter(
        self,
        channel_id: int,
        filter_type: int,
        mask: bytes,
        pattern: bytes,
        flow_control: bytes | None = None,
    ) -> int:
        raise J2534Error("WindowsJ2534Device not yet implemented")

    def ioctl(self, channel_id: int, ioctl_id: int, input_arg: Any, output_arg: Any) -> None:
        raise J2534Error("WindowsJ2534Device not yet implemented")
