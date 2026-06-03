"""CanusbSource -- LAWICEL/CANUSB adapter. Phase-2."""

from __future__ import annotations

from typing import TYPE_CHECKING

from SAAB_SUITE.ports.can_source import CanSourceStats, ICanSource

if TYPE_CHECKING:
    from collections.abc import Iterator

    from SAAB_SUITE.domain.can.bus import CanBus
    from SAAB_SUITE.domain.can.frame import CanFilter, CanFrame


class CanusbSource(ICanSource):
    """LAWICEL/CANUSB serial-over-USB adapter."""

    def __init__(self, port: str) -> None:
        self.port = port

    def open(self, bus: CanBus, bitrate: int) -> None:
        raise NotImplementedError("CANUSB adapter not yet implemented")

    def close(self) -> None:
        raise NotImplementedError

    def read(self, timeout_ms: int) -> CanFrame | None:
        raise NotImplementedError

    def iter_frames(self) -> Iterator[CanFrame]:
        raise NotImplementedError

    def filter(self, mask: CanFilter) -> None:
        raise NotImplementedError

    @property
    def stats(self) -> CanSourceStats:
        raise NotImplementedError
