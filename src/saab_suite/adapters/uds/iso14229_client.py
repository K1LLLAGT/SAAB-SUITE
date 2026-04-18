"""ISO 14229 UDS client over an IIsoTpTransport."""

from __future__ import annotations

from saab_suite.kernel.errors import UdsError
from saab_suite.kernel.types import WirePayload
from saab_suite.ports.isotp import IIsoTpTransport
from saab_suite.ports.uds import IUdsClient


class Iso14229Client(IUdsClient):
    """UDS client. Phase-2."""

    def __init__(self, transport: IIsoTpTransport) -> None:
        self.transport = transport

    def diagnostic_session_control(self, session_type: int) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def ecu_reset(self, reset_type: int) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def security_access(self, level: int, key: WirePayload | None = None) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def read_data_by_identifier(self, did: int) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def write_data_by_identifier(self, did: int, data: WirePayload) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def read_dtc_information(self, sub_function: int, status_mask: int = 0xFF) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def clear_diagnostic_information(self, group: int = 0xFFFFFF) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def request_download(self, address: int, size: int) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def transfer_data(self, block_seq_counter: int, data: WirePayload) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def request_transfer_exit(self) -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def routine_control(self, sub_function: int, routine_id: int, data: WirePayload = b"") -> WirePayload:
        raise UdsError("UDS client not yet implemented")

    def tester_present(self, suppress_response: bool = True) -> WirePayload:
        raise UdsError("UDS client not yet implemented")
