from __future__ import annotations

import time
from dataclasses import dataclass

from saab_suite.adapters.can.remote_interface import CanFrame, RemoteCanInterface

# ISO-TP PCI type nibbles (high nibble of byte 0)
_PCI_SF = 0x0  # Single Frame
_PCI_FF = 0x1  # First Frame
_PCI_CF = 0x2  # Consecutive Frame
_PCI_FC = 0x3  # Flow Control (we send this to the ECU during a multi-frame read)

# UDS
_NEGATIVE_RESPONSE = 0x7F


def _pad8(data: bytes) -> bytes:
    """Pad a CAN payload out to 8 bytes (classic CAN frames are fixed-length)."""
    return data + b"\x00" * (8 - len(data))


@dataclass
class UdsResponse:
    """An assembled UDS response.

    `raw` is the full UDS message with all ISO-TP framing removed, e.g.
    ``62 F1 90 <vin bytes...>`` for a positive ReadDataByIdentifier, or
    ``7F 22 31`` for a negative response.
    """

    raw: bytes

    @property
    def service(self) -> int:
        """The response service byte (0x7F for a negative response)."""
        return self.raw[0]

    @property
    def is_negative(self) -> bool:
        """Return the is negative."""
        return bool(self.raw) and self.raw[0] == _NEGATIVE_RESPONSE

    @property
    def nrc(self) -> int | None:
        """Negative-response code, or None for a positive response."""
        return self.raw[2] if self.is_negative and len(self.raw) >= 3 else None

    @property
    def data(self) -> bytes:
        """Payload after the service byte (and the 2-byte DID for 0x62)."""
        if self.is_negative:
            return b""
        # ReadDataByIdentifier positive response: strip 0x62 + 2-byte DID
        if self.raw and self.raw[0] == 0x62 and len(self.raw) >= 3:
            return self.raw[3:]
        return self.raw[1:]


class UdsClient:
    """Small UDS client over a single CAN ID pair, with ISO-TP (ISO 15765-2).

    Handles single-frame and multi-frame responses. Block size / STmin are
    fixed at 0 in the flow-control frame we emit, i.e. the ECU may send all
    consecutive frames back-to-back, which is fine for diagnostic reads.
    """

    def __init__(self, req_id: int, res_id: int, timeout: float = 1.0):
        self.req_id = req_id
        self.res_id = res_id
        self.timeout = timeout
        self._iface = RemoteCanInterface()

    def __enter__(self) -> UdsClient:
        """Return the context manager instance."""
        self._iface.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Close the context manager."""
        self._iface.close()

    # -- public API ------------------------------------------------------
    def read_data_by_identifier(self, did: int) -> UdsResponse:
        # UDS service 0x22 ReadDataByIdentifier
        """Read data by identifier."""
        self._send_request(bytes([0x22, (did >> 8) & 0xFF, did & 0xFF]))
        return UdsResponse(raw=self._recv_response())

    # -- ISO-TP send (request is always a single frame here) -------------
    def _send_request(self, service_payload: bytes) -> None:
        if len(service_payload) > 7:
            raise ValueError("multi-frame requests are not supported")
        sf = bytes([(_PCI_SF << 4) | len(service_payload)]) + service_payload
        self._iface.send(CanFrame(can_id=self.req_id, data=_pad8(sf)))

    # -- ISO-TP receive --------------------------------------------------
    def _recv_response(self) -> bytes:
        deadline = time.time() + self.timeout
        first = self._await_frame(deadline)
        pci_type = first[0] >> 4

        if pci_type == _PCI_SF:
            length = first[0] & 0x0F
            return first[1 : 1 + length]

        if pci_type == _PCI_FF:
            total = ((first[0] & 0x0F) << 8) | first[1]
            buf = bytearray(first[2:8])
            # tell the ECU it is clear to send all remaining frames
            fc = bytes([(_PCI_FC << 4) | 0x00, 0x00, 0x00])
            self._iface.send(CanFrame(can_id=self.req_id, data=_pad8(fc)))
            expected_seq = 1
            while len(buf) < total:
                cf = self._await_frame(deadline)
                if (cf[0] >> 4) != _PCI_CF:
                    continue
                if (cf[0] & 0x0F) != (expected_seq & 0x0F):
                    raise OSError(
                        f"ISO-TP out-of-order frame: got {cf[0] & 0x0F}, "
                        f"expected {expected_seq & 0x0F}"
                    )
                buf.extend(cf[1:8])
                expected_seq += 1
            return bytes(buf[:total])

        raise OSError(f"unexpected ISO-TP PCI on first frame: 0x{pci_type:X}")

    def _await_frame(self, deadline: float) -> bytes:
        """Block until a frame on res_id arrives or the deadline passes."""
        while time.time() < deadline:
            rx = self._iface.recv(timeout=0.05)
            if rx is None or rx.can_id != self.res_id:
                continue
            return rx.data
        raise TimeoutError("No UDS response received")
