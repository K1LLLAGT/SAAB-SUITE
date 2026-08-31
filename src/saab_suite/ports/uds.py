"""UDS client port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.kernel.types import WirePayload


class IUdsClient(Protocol):
    """Define the high-level ISO 14229 client interface."""

    def diagnostic_session_control(self, session_type: int) -> WirePayload:
        """Request a UDS diagnostic session."""
        ...

    def ecu_reset(self, reset_type: int) -> WirePayload:
        """Request an ECU reset."""
        ...

    def security_access(self, level: int, key: WirePayload | None = None) -> WirePayload:
        """Request UDS security access."""
        ...

    def read_data_by_identifier(self, did: int) -> WirePayload:
        """Read a DID value."""
        ...

    def write_data_by_identifier(self, did: int, data: WirePayload) -> WirePayload:
        """Write a DID value."""
        ...

    def read_dtc_information(self, sub_function: int, status_mask: int = 0xFF) -> WirePayload:
        """Read DTC information."""
        ...

    def clear_diagnostic_information(self, group: int = 0xFFFFFF) -> WirePayload:
        """Clear DTC information for a group."""
        ...

    def request_download(self, address: int, size: int) -> WirePayload:
        """Request a download session for an address range."""
        ...

    def transfer_data(self, block_seq_counter: int, data: WirePayload) -> WirePayload:
        """Transfer a block of download data."""
        ...

    def request_transfer_exit(self) -> WirePayload:
        """Request transfer exit."""
        ...

    def routine_control(
        self,
        sub_function: int,
        routine_id: int,
        data: WirePayload = b"",
    ) -> WirePayload:
        """Run a UDS routine control command."""
        ...

    def tester_present(self, suppress_response: bool = True) -> WirePayload:
        """Send a tester-present request."""
        ...
