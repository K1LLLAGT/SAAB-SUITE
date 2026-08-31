"""PyCanBackend -- python-can backend implementing both ICanSource and ICanSink.

python-can already speaks SocketCAN *and* SLCAN/CANUSB (and pcan, etc.) via its
`interface` selector, so this single class realizes both the socketcan_source
and canusb_source Phase-2 stubs. Pick the concrete transport via runtime config.
J2534 is NOT python-can; that stays a separate backend over IJ2534Device.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, cast

from saab_suite.domain.can.frame import CanFrame, CanId
from saab_suite.ports.can_source import CanSourceStats

try:
    import can
except ImportError:
    can = None

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from saab_suite.domain.can.bus import CanBus
    from saab_suite.domain.can.frame import CanFilter
    from saab_suite.kernel.types import MonotonicNs


class PyCanBackend:
    """Implements ICanSource + ICanSink over python-can."""

    def __init__(
        self,
        channel: str,
        interface: str,
        clock: Callable[[], int] = time.monotonic_ns,
    ) -> None:
        self._channel = channel
        self._interface = interface
        self._clock = clock
        self._bus_obj: can.BusABC | None = None
        self._bus: CanBus | None = None
        self._frames_read = 0
        self._bytes_read = 0

    # -- lifecycle (ICanSource) -----------------------------------------------
    def open(self, bus: CanBus, bitrate: int) -> None:
        """Open the resource."""
        if can is None:
            raise RuntimeError("python-can not installed. Install saab_suite[hardware].")
        self._bus = bus
        self._bus_obj = can.Bus(channel=self._channel, interface=self._interface, bitrate=bitrate)

    def close(self) -> None:
        """Close the resource."""
        if self._bus_obj is not None:
            self._bus_obj.shutdown()
            self._bus_obj = None

    # -- read side (ICanSource) -----------------------------------------------
    def read(self, timeout_ms: int) -> CanFrame | None:
        """Read."""
        if self._bus_obj is None or self._bus is None:
            raise RuntimeError("backend not open")
        msg = self._bus_obj.recv(timeout_ms / 1000.0)
        if msg is None:
            return None
        data = bytes(msg.data)
        self._frames_read += 1
        self._bytes_read += len(data)
        return CanFrame(
            timestamp=cast("MonotonicNs", self._clock()),
            bus=self._bus,
            can_id=cast("CanId", msg.arbitration_id),
            is_extended=bool(msg.is_extended_id),
            is_fd=bool(getattr(msg, "is_fd", False)),
            dlc=len(data),
            data=data,
        )

    def iter_frames(self) -> Iterator[CanFrame]:
        """Iterate over frames."""
        while True:
            frame = self.read(timeout_ms=100)
            if frame is not None:
                yield frame

    def filter(self, mask: CanFilter) -> None:
        """Filter."""
        if self._bus_obj is None:
            raise RuntimeError("backend not open")
        self._bus_obj.set_filters(
            [{"can_id": int(mask.can_id), "can_mask": mask.mask, "extended": mask.is_extended}]
        )

    @property
    def stats(self) -> CanSourceStats:
        """Return the stats."""
        return CanSourceStats(
            frames_read=self._frames_read, bytes_read=self._bytes_read, bus_errors=0, overruns=0
        )

    # -- write side (ICanSink) ------------------------------------------------
    def write(self, frame: CanFrame) -> None:
        """Write."""
        if self._bus_obj is None:
            raise RuntimeError("backend not open")
        self._bus_obj.send(
            can.Message(
                arbitration_id=int(frame.can_id),
                data=frame.data,
                is_extended_id=frame.is_extended,
                is_fd=frame.is_fd,
            )
        )

    def flush(self) -> None:
        """Flush."""
        if self._bus_obj is not None:
            self._bus_obj.flush_tx_buffer()
