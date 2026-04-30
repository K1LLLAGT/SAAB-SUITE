"""ICanSource -- read CAN frames from any transport."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterator

    from saab_suite.domain.can.bus import CanBus
    from saab_suite.domain.can.frame import CanFilter, CanFrame


@dataclass(frozen=True, slots=True)
class CanSourceStats:
    """Throughput and error counters for an ICanSource."""

    frames_read: int
    bytes_read: int
    bus_errors: int
    overruns: int


class ICanSource(Protocol):
    """A source of CAN frames."""

    def open(self, bus: CanBus, bitrate: int) -> None: ...
    def close(self) -> None: ...
    def read(self, timeout_ms: int) -> CanFrame | None: ...
    def iter_frames(self) -> Iterator[CanFrame]: ...
    def filter(self, mask: CanFilter) -> None: ...
    @property
    def stats(self) -> CanSourceStats: ...
