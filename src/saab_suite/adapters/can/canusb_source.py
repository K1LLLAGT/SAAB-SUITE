"""CanusbSource -- LAWICEL/CANUSB adapter. Phase-2."""

from __future__ import annotations

from collections.abc import Iterator

from saab_suite.domain.can.bus import CanBus
from saab_suite.domain.can.frame import CanFilter, CanFrame
from saab_suite.ports.can_source import CanSourceStats, ICanSource


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
