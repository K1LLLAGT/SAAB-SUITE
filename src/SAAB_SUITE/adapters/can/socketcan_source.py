"""SocketCanSource -- Linux SocketCAN."""

from __future__ import annotations

from typing import TYPE_CHECKING

from SAAB_SUITE.ports.can_source import CanSourceStats, ICanSource

if TYPE_CHECKING:
    from collections.abc import Iterator

    from SAAB_SUITE.domain.can.bus import CanBus
    from SAAB_SUITE.domain.can.frame import CanFilter, CanFrame


class SocketCanSource(ICanSource):
    """SocketCAN-backed source. Linux only. Phase-2."""

    def __init__(self, interface: str = "can0") -> None:
        self.interface = interface

    def open(self, bus: CanBus, bitrate: int) -> None:
        raise NotImplementedError("SocketCAN adapter not yet implemented")

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
