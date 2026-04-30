"""ISO 14230 KWP2000 client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from saab_suite.kernel.errors import KwpError
from saab_suite.ports.kwp2000 import IKwpClient

if TYPE_CHECKING:
    from saab_suite.kernel.types import WirePayload


class Iso14230Client(IKwpClient):
    """KWP2000 client. Phase-2."""

    def start_diagnostic_session(self, session_type: int) -> WirePayload:
        raise KwpError("KWP client not yet implemented")

    def stop_diagnostic_session(self) -> WirePayload:
        raise KwpError("KWP client not yet implemented")

    def read_dtc_by_status(self, status: int = 0x00) -> WirePayload:
        raise KwpError("KWP client not yet implemented")

    def clear_diagnostic_information(self, group: int = 0xFF00) -> WirePayload:
        raise KwpError("KWP client not yet implemented")

    def read_data_by_local_id(self, local_id: int) -> WirePayload:
        raise KwpError("KWP client not yet implemented")

    def tester_present(self, suppress_response: bool = True) -> WirePayload:
        raise KwpError("KWP client not yet implemented")
