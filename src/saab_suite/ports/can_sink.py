"""ICanSink -- write CAN frames to any transport."""

from __future__ import annotations

from typing import Protocol

from saab_suite.domain.can.frame import CanFrame


class ICanSink(Protocol):
    """A sink for CAN frames."""

    def write(self, frame: CanFrame) -> None: ...
    def flush(self) -> None: ...
