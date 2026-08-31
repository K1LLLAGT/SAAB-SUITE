"""Linux can-isotp socket adapter. Higher performance than software impl."""

from __future__ import annotations

from typing import TYPE_CHECKING

from saab_suite.kernel.errors import IsoTpError
from saab_suite.ports.isotp import IIsoTpTransport

if TYPE_CHECKING:
    from saab_suite.domain.ecu.address import CanAddressPair
    from saab_suite.kernel.types import WirePayload


class KernelIsoTp(IIsoTpTransport):
    """Linux can-isotp adapter. Phase-2."""

    def __init__(self, interface: str = "can0") -> None:
        self.interface = interface

    def open(self, addresses: CanAddressPair) -> None:
        """Open the resource."""
        raise IsoTpError("kernel ISO-TP not yet implemented")

    def close(self) -> None:
        """Close the resource."""
        raise IsoTpError("kernel ISO-TP not yet implemented")

    def send(self, payload: WirePayload, timeout_ms: int) -> None:
        """Send the requested payload."""
        raise IsoTpError("kernel ISO-TP not yet implemented")

    def recv(self, timeout_ms: int) -> WirePayload:
        """Receive the next payload."""
        raise IsoTpError("kernel ISO-TP not yet implemented")
