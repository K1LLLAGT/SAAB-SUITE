"""ISO-TP port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.domain.ecu.address import CanAddressPair
    from saab_suite.kernel.types import WirePayload


class IIsoTpTransport(Protocol):
    """Define the ISO-TP request and response transport interface."""

    def open(self, addresses: CanAddressPair) -> None:
        """Open the transport for a request and response address pair."""
        ...

    def close(self) -> None:
        """Close the transport."""
        ...

    def send(self, payload: WirePayload, timeout_ms: int) -> None:
        """Send a payload over ISO-TP."""
        ...

    def recv(self, timeout_ms: int) -> WirePayload:
        """Receive the next ISO-TP payload."""
        ...
