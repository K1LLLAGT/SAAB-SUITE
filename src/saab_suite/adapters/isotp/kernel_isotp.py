"""Linux can-isotp socket adapter. Higher performance than software impl."""

from __future__ import annotations

from saab_suite.domain.ecu.address import CanAddressPair
from saab_suite.kernel.errors import IsoTpError
from saab_suite.kernel.types import WirePayload
from saab_suite.ports.isotp import IIsoTpTransport


class KernelIsoTp(IIsoTpTransport):
    """Linux can-isotp adapter. Phase-2."""

    def __init__(self, interface: str = "can0") -> None:
        self.interface = interface

    def open(self, addresses: CanAddressPair) -> None:
        raise IsoTpError("kernel ISO-TP not yet implemented")

    def close(self) -> None:
        raise IsoTpError("kernel ISO-TP not yet implemented")

    def send(self, payload: WirePayload, timeout_ms: int) -> None:
        raise IsoTpError("kernel ISO-TP not yet implemented")

    def recv(self, timeout_ms: int) -> WirePayload:
        raise IsoTpError("kernel ISO-TP not yet implemented")
