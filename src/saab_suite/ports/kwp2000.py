"""KWP2000 port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.kernel.types import WirePayload


class IKwpClient(Protocol):
    """Define the legacy KWP2000 client interface."""

    def start_diagnostic_session(self, session_type: int) -> WirePayload:
        """Start a KWP2000 diagnostic session."""
        ...

    def stop_diagnostic_session(self) -> WirePayload:
        """Stop the active KWP2000 diagnostic session."""
        ...

    def read_dtc_by_status(self, status: int = 0x00) -> WirePayload:
        """Read DTCs matching a status mask."""
        ...

    def clear_diagnostic_information(self, group: int = 0xFF00) -> WirePayload:
        """Clear diagnostic information for a group."""
        ...

    def read_data_by_local_id(self, local_id: int) -> WirePayload:
        """Read a local-identifier data record."""
        ...

    def tester_present(self, suppress_response: bool = True) -> WirePayload:
        """Send a tester-present request."""
        ...
