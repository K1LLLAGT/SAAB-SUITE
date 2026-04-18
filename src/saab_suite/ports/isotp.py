"""IIsoTpTransport -- ISO 15765-2 transport."""

from __future__ import annotations

from typing import Protocol

from saab_suite.domain.ecu.address import CanAddressPair
from saab_suite.kernel.types import WirePayload


class IIsoTpTransport(Protocol):
    """ISO-TP request/response transport over a CAN source/sink pair."""

    def open(self, addresses: CanAddressPair) -> None: ...
    def close(self) -> None: ...
    def send(self, payload: WirePayload, timeout_ms: int) -> None: ...
    def recv(self, timeout_ms: int) -> WirePayload: ...
