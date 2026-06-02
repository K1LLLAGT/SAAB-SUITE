from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import can
from saab_suite.remote_tcp_bus import RemoteTcpBus
from saab_suite.runtime.can_config import load_can_config


@dataclass
class CanFrame:
    can_id: int
    data: bytes


class RemoteCanInterface:
    """CAN interface supporting remote, virtual, and mock modes."""

    def __init__(self):
        self._cfg = load_can_config()
        self._bus = None

    def open(self):
        if self._cfg.mode == "mock":
            return

        if self._cfg.mode == "remote":
            self._bus = RemoteTcpBus(
                host=self._cfg.remote_host,
                port=self._cfg.remote_port,
                timeout=1.0,
            )
            return

        if self._cfg.mode == "virtual":
            self._bus = can.interface.Bus(
                channel=self._cfg.virtual_channel,
                bustype="virtual",
            )
            return

        raise RuntimeError(f"Unsupported CAN mode: {self._cfg.mode}")

    def close(self):
        if self._bus is not None:
            try:
                self._bus.close()
            finally:
                self._bus = None

    def send(self, frame: CanFrame):
        if self._cfg.mode == "mock":
            return
        if self._bus is None:
            raise RuntimeError("CAN interface not open")

        msg = can.Message(
            arbitration_id=frame.can_id,
            data=frame.data,
            is_extended_id=True,
        )
        self._bus.send(msg)

    def recv(self, timeout: float = 0.1) -> Optional[CanFrame]:
        if self._cfg.mode == "mock":
            return None
        if self._bus is None:
            raise RuntimeError("CAN interface not open")

        msg = self._bus.recv(timeout)
        if msg is None:
            return None

        return CanFrame(can_id=msg.arbitration_id, data=bytes(msg.data))
