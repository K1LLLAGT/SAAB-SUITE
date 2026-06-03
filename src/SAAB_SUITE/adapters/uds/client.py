"""UdsClient -- ISO 14229 client over an IIsoTpTransport.

Implements ports.uds.IUdsClient. Each method builds a request payload, sends it
through the ISO-TP transport, and returns the raw response WirePayload. Negative
responses (0x7F ...) are returned as-is for the caller to interpret, EXCEPT the
"response pending" NRC 0x78, which is transparently waited out.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from SAAB_SUITE.kernel.types import WirePayload
    from SAAB_SUITE.ports.isotp import IIsoTpTransport

_NEGATIVE = 0x7F
_NRC_RESPONSE_PENDING = 0x78


class UdsClient:
    def __init__(self, transport: "IIsoTpTransport", timeout_ms: int = 2000) -> None:
        self._t = transport
        self._timeout = timeout_ms

    def _request(self, payload: bytes) -> "WirePayload":
        self._t.send(cast("WirePayload", payload), self._timeout)
        resp = bytes(self._t.recv(self._timeout))
        while len(resp) >= 3 and resp[0] == _NEGATIVE and resp[2] == _NRC_RESPONSE_PENDING:
            resp = bytes(self._t.recv(self._timeout))
        return cast("WirePayload", resp)

    # -- ISO 14229 services ---------------------------------------------------
    def diagnostic_session_control(self, session_type: int) -> "WirePayload":
        return self._request(bytes([0x10, session_type & 0xFF]))

    def ecu_reset(self, reset_type: int) -> "WirePayload":
        return self._request(bytes([0x11, reset_type & 0xFF]))

    def security_access(self, level: int, key: "WirePayload | None" = None) -> "WirePayload":
        return self._request(bytes([0x27, level & 0xFF]) + (bytes(key) if key else b""))

    def read_data_by_identifier(self, did: int) -> "WirePayload":
        return self._request(bytes([0x22, (did >> 8) & 0xFF, did & 0xFF]))

    def write_data_by_identifier(self, did: int, data: "WirePayload") -> "WirePayload":
        return self._request(bytes([0x2E, (did >> 8) & 0xFF, did & 0xFF]) + bytes(data))

    def read_dtc_information(self, sub_function: int, status_mask: int = 0xFF) -> "WirePayload":
        return self._request(bytes([0x19, sub_function & 0xFF, status_mask & 0xFF]))

    def clear_diagnostic_information(self, group: int = 0xFFFFFF) -> "WirePayload":
        return self._request(bytes([0x14, (group >> 16) & 0xFF, (group >> 8) & 0xFF, group & 0xFF]))

    def request_download(self, address: int, size: int) -> "WirePayload":
        # dataFormatId 0x00, addressAndLengthFormatId 0x44 (4-byte addr + 4-byte size)
        return self._request(
            bytes([0x34, 0x00, 0x44]) + address.to_bytes(4, "big") + size.to_bytes(4, "big")
        )

    def transfer_data(self, block_seq_counter: int, data: "WirePayload") -> "WirePayload":
        return self._request(bytes([0x36, block_seq_counter & 0xFF]) + bytes(data))

    def request_transfer_exit(self) -> "WirePayload":
        return self._request(bytes([0x37]))

    def routine_control(self, sub_function: int, routine_id: int, data: "WirePayload" = b"") -> "WirePayload":
        return self._request(
            bytes([0x31, sub_function & 0xFF, (routine_id >> 8) & 0xFF, routine_id & 0xFF]) + bytes(data)
        )

    def tester_present(self, suppress_response: bool = True) -> "WirePayload":
        return self._request(bytes([0x3E, 0x80 if suppress_response else 0x00]))
