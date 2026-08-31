"""J2534CanSource -- wraps an IJ2534Device as an ICanSource."""

from __future__ import annotations

from typing import TYPE_CHECKING

from saab_suite.ports.can_source import CanSourceStats, ICanSource

if TYPE_CHECKING:
    from collections.abc import Iterator

    from saab_suite.domain.can.bus import CanBus
    from saab_suite.domain.can.frame import CanFilter, CanFrame
    from saab_suite.ports.j2534 import IJ2534Device


class J2534CanSource(ICanSource):
    """ICanSource over a J2534 device. Phase-2."""

    def __init__(self, device: IJ2534Device) -> None:
        self.device = device

    def open(self, bus: CanBus, bitrate: int) -> None:
        """Open the resource."""
        raise NotImplementedError("J2534 source not yet implemented")

    def close(self) -> None:
        """Close the resource."""
        raise NotImplementedError

    def read(self, timeout_ms: int) -> CanFrame | None:
        """Read."""
        raise NotImplementedError

    def iter_frames(self) -> Iterator[CanFrame]:
        """Iterate over frames."""
        raise NotImplementedError

    def filter(self, mask: CanFilter) -> None:
        """Filter."""
        raise NotImplementedError

    @property
    def stats(self) -> CanSourceStats:
        """Return the stats."""
        raise NotImplementedError
