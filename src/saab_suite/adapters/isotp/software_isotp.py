"""Pure-Python ISO 15765-2 implementation. Cross-platform."""

from __future__ import annotations

from saab_suite.domain.ecu.address import CanAddressPair
from saab_suite.kernel.errors import IsoTpError
from saab_suite.kernel.types import WirePayload
from saab_suite.ports.can_sink import ICanSink
from saab_suite.ports.can_source import ICanSource
from saab_suite.ports.isotp import IIsoTpTransport


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
