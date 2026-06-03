import socket
import struct
import select
from typing import Optional

import can  # only for can.Message class


# 16‑byte CAN frame over TCP:
#   uint32  can_id
#   uint8   dlc
#   uint8   flags
#   uint8   rsv1
#   uint8   rsv2
#   8 bytes data
FRAME_STRUCT = struct.Struct("!IBBBB8s")

FLAG_EXT = 0x01
FLAG_FD  = 0x02
FLAG_RTR = 0x04


class RemoteTcpBus:
    """
    Drop‑in replacement for python‑can's RemoteBus.
    Works on Python 3.13, Termux, Android.
    """

    def __init__(self, host: str, port: int, timeout: float = 1.0):
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._sock.setblocking(False)
        self._timeout = timeout

    # ------------------------------------------------------------
    # Public API (mirrors python‑can Bus semantics)
    # ------------------------------------------------------------

    def send(self, msg: can.Message) -> None:
        frame = self._encode(msg)
        self._sock.sendall(frame)

    def recv(self, timeout: Optional[float] = None) -> Optional[can.Message]:
        if timeout is None:
            timeout = self._timeout

        r, _, _ = select.select([self._sock], [], [], timeout)
        if not r:
            return None

        raw = self._recv_exact(FRAME_STRUCT.size)
        if not raw:
            return None

        return self._decode(raw)

    def close(self) -> None:
        try:
            self._sock.close()
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------

    def _recv_exact(self, n: int) -> Optional[bytes]:
        buf = bytearray()
        while len(buf) < n:
            try:
                chunk = self._sock.recv(n - len(buf))
            except BlockingIOError:
                continue
            if not chunk:
                return None
            buf.extend(chunk)
        return bytes(buf)

    def _encode(self, msg: can.Message) -> bytes:
        can_id = msg.arbitration_id & 0x1FFFFFFF
        dlc = msg.dlc

        flags = 0
        if msg.is_extended_id:
            flags |= FLAG_EXT
        if getattr(msg, "is_fd", False):
            flags |= FLAG_FD
        if msg.is_remote_frame:
            flags |= FLAG_RTR

        data = (msg.data or b"")[:8].ljust(8, b"\x00")

        return FRAME_STRUCT.pack(can_id, dlc, flags, 0, 0, data)

    def _decode(self, raw: bytes) -> can.Message:
        can_id, dlc, flags, _r1, _r2, data = FRAME_STRUCT.unpack(raw)

        return can.Message(
            arbitration_id=can_id,
            is_extended_id=bool(flags & FLAG_EXT),
            is_fd=bool(flags & FLAG_FD),
            is_remote_frame=bool(flags & FLAG_RTR),
            data=data[:dlc],
            dlc=dlc,
        )
