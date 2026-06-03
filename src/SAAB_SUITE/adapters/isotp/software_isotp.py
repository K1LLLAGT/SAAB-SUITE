"""Pure-Python ISO 15765-2 implementation. Cross-platform."""

from __future__ import annotations

from typing import TYPE_CHECKING

from SAAB_SUITE.kernel.errors import IsoTpError
from SAAB_SUITE.ports.isotp import IIsoTpTransport

if TYPE_CHECKING:
    from SAAB_SUITE.domain.ecu.address import CanAddressPair
    from SAAB_SUITE.kernel.types import WirePayload
    from SAAB_SUITE.ports.can_sink import ICanSink
    from SAAB_SUITE.ports.can_source import ICanSource


class SoftwareIsoTp(IIsoTpTransport):
    """Pure-Python ISO-TP. Phase-2."""

    def __init__(self, source: ICanSource, sink: ICanSink) -> None:
        self.source = source
        self.sink = sink

    def open(self, addresses: CanAddressPair) -> None:
        raise IsoTpError("software ISO-TP not yet implemented")

    def close(self) -> None:
        raise IsoTpError("software ISO-TP not yet implemented")

    def send(self, payload: WirePayload, timeout_ms: int) -> None:
        raise IsoTpError("software ISO-TP not yet implemented")

    def recv(self, timeout_ms: int) -> WirePayload:
        raise IsoTpError("software ISO-TP not yet implemented")
