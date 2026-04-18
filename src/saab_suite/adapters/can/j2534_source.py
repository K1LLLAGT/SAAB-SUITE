"""J2534CanSource -- wraps an IJ2534Device as an ICanSource."""

from __future__ import annotations

from collections.abc import Iterator

from saab_suite.domain.can.bus import CanBus
from saab_suite.domain.can.frame import CanFilter, CanFrame
from saab_suite.ports.can_source import CanSourceStats, ICanSource
from saab_suite.ports.j2534 import IJ2534Device


class J2534CanSource(ICanSource):
    """ICanSource over a J2534 device. Phase-2."""

    def __init__(self, device: IJ2534Device) -> None:
        self.device = device

    def open(self, bus: CanBus, bitrate: int) -> None:
        raise NotImplementedError("J2534 source not yet implemented")

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
