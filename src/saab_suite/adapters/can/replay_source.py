from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from saab_suite.runtime import paths

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@dataclass
class ReplayFrame:
    """Represent replay frame."""
    timestamp: float
    can_id: int
    data: bytes


class ReplayCanSource:
    """Simple CAN replay source reading from a line-based log file.

    Format (per line):
        <timestamp> <hex_id> <hex_bytes>

    Example:
        0.000 18DAF110 0227103B
    """

    def __init__(self, file: Path) -> None:
        self._file = file

    @classmethod
    def from_name(cls, name: str) -> ReplayCanSource:
        """Resolve a replay file from the runtime replay directory."""
        base = paths.replay()
        return cls(base / name)

    def frames(self) -> Iterator[ReplayFrame]:
        """Frames."""
        with self._file.open("r", encoding="utf8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                ts_s, can_id_s, data_s = line.split(maxsplit=2)
                yield ReplayFrame(
                    timestamp=float(ts_s),
                    can_id=int(can_id_s, 16),
                    data=bytes.fromhex(data_s),
                )

    def __iter__(self) -> Iterator[ReplayFrame]:
        """Iterate over the available items."""
        return self.frames()
