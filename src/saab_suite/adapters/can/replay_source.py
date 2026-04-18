"""ReplayCanSource -- read frames from an NDJSON log."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from saab_suite.domain.can.bus import CanBus
from saab_suite.domain.can.frame import CanFilter, CanFrame
from saab_suite.ports.can_source import CanSourceStats, ICanSource


class ReplayCanSource(ICanSource):
    """Replay frames from an NDJSON log file. One frame per line."""

    def __init__(self, path: Path, speed: float = 1.0) -> None:
        self.path = path
        self.speed = speed

    def open(self, bus: CanBus, bitrate: int) -> None:
        raise NotImplementedError("replay adapter not yet implemented")

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
