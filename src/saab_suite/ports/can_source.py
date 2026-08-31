"""CAN source port definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator

    from saab_suite.domain.can.bus import CanBus
    from saab_suite.domain.can.frame import CanFilter, CanFrame


@dataclass(frozen=True, slots=True)
class CanSourceStats:
    """Track CAN source throughput and error counters."""

    frames_read: int
    bytes_read: int
    bus_errors: int
    overruns: int


class ICanSource(Protocol):
    """Define the CAN frame source interface."""

    def open(self, bus: CanBus, bitrate: int) -> None:
        """Open the source for a specific bus and bitrate."""
        ...

    def close(self) -> None:
        """Close the source."""
        ...

    def read(self, timeout_ms: int) -> CanFrame | None:
        """Read the next frame if one arrives before the timeout."""
        ...

    def iter_frames(self) -> Iterator[CanFrame]:
        """Iterate over frames from the source."""
        ...

    def filter(self, mask: CanFilter) -> None:
        """Apply a hardware or software receive filter."""
        ...

    @property
    def stats(self) -> CanSourceStats:
        """Return source statistics."""
        ...
