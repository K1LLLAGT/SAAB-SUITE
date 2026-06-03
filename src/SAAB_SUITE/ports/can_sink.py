"""ICanSink -- write CAN frames to any transport."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from SAAB_SUITE.domain.can.frame import CanFrame


class ICanSink(Protocol):
    """A sink for CAN frames."""

    def write(self, frame: CanFrame) -> None: ...
    def flush(self) -> None: ...
