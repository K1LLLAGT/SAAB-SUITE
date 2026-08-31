"""CAN sink port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.domain.can.frame import CanFrame


class ICanSink(Protocol):
    """Define the CAN frame sink interface."""

    def write(self, frame: CanFrame) -> None:
        """Write a frame to the transport."""
        ...

    def flush(self) -> None:
        """Flush any buffered outbound frames."""
        ...
