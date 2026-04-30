"""MockCanSource -- deterministic, scriptable; for tests and dev."""

from __future__ import annotations

from typing import TYPE_CHECKING

from saab_suite.ports.can_source import CanSourceStats, ICanSource

if TYPE_CHECKING:
    from collections.abc import Iterator

    from saab_suite.domain.can.bus import CanBus
    from saab_suite.domain.can.frame import CanFilter, CanFrame


class MockCanSource(ICanSource):
    """In-memory CAN source. Yields a scripted frame list."""

    def __init__(self, frames: list[CanFrame] | None = None) -> None:
        self._frames: list[CanFrame] = list(frames or [])
        self._open = False
        self._stats = CanSourceStats(0, 0, 0, 0)

    def open(self, bus: CanBus, bitrate: int) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def read(self, timeout_ms: int) -> CanFrame | None:
        if not self._frames:
            return None
        frame = self._frames.pop(0)
        self._stats = CanSourceStats(
            self._stats.frames_read + 1,
            self._stats.bytes_read + len(frame.data),
            self._stats.bus_errors,
            self._stats.overruns,
        )
        return frame

    def iter_frames(self) -> Iterator[CanFrame]:
        while self._frames:
            yield self._frames.pop(0)

    def filter(self, mask: CanFilter) -> None:
        pass

    @property
    def stats(self) -> CanSourceStats:
        return self._stats
