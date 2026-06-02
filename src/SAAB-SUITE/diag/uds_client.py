from __future__ import annotations

import time
from dataclasses import dataclass

from saab_suite.adapters.can.remote_interface import RemoteCanInterface, CanFrame


@dataclass
class UdsResponse:
    raw: bytes


class UdsClient:
    """Very small UDS client over a single CAN ID pair (no ISO-TP yet)."""

    def __init__(self, req_id: int, res_id: int, timeout: float = 1.0):
        self.req_id = req_id
        self.res_id = res_id
        self.timeout = timeout
        self._iface = RemoteCanInterface()

    def __enter__(self) -> "UdsClient":
        self._iface.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._iface.close()

    def read_data_by_identifier(self, did: int) -> UdsResponse:
        # UDS: 0x22 <DID_hi> <DID_lo>
        payload = bytes([0x22, (did >> 8) & 0xFF, did & 0xFF])
        frame = CanFrame(can_id=self.req_id, data=payload)
        self._iface.send(frame)

        deadline = time.time() + self.timeout
        while time.time() < deadline:
            rx = self._iface.recv(timeout=0.05)
            if rx is None:
                continue
            if rx.can_id != self.res_id:
                continue
            return UdsResponse(raw=rx.data)

        raise TimeoutError("No UDS response received")
