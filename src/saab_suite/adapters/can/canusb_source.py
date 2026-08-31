"""CanusbSource -- LAWICEL/CANUSB adapter. Phase-2."""

from __future__ import annotations

from typing import TYPE_CHECKING

from saab_suite.ports.can_source import CanSourceStats, ICanSource

if TYPE_CHECKING:
    from collections.abc import Iterator

    from saab_suite.domain.can.bus import CanBus
    from saab_suite.domain.can.frame import CanFilter, CanFrame


class CanusbSource(ICanSource):
    """LAWICEL/CANUSB serial-over-USB adapter."""

    def __init__(self, port: str) -> None:
        self.port = port

    def open(self, bus: CanBus, bitrate: int) -> None:
        """Open the resource."""
        raise NotImplementedError("CANUSB adapter not yet implemented")

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
