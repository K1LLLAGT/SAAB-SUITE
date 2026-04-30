import socket
import struct
import select
from typing import Optional

import can  # python-can >= 4.x is fine for Message class


# Frame format (big-endian):
#   uint32  can_id
#   uint8   dlc
#   uint8   flags (bit 0: is_extended_id, bit 1: is_fd, bit 2: is_remote_frame)
#   uint8   reserved (0)
#   uint8   reserved (0)
#   8 bytes data (padded with zeros if dlc < 8)
#
# Total: 4 + 1 + 1 + 1 + 1 + 8 = 16 bytes per frame
FRAME_STRUCT = struct.Struct("!IBBBB8s")

FLAG_EXTENDED = 0x01
FLAG_FD       = 0x02
FLAG_RTR      = 0x04


class RemoteTcpBus:
    """
    Minimal TCP CAN bus replacement for python-can's RemoteBus.

    Expected to talk to a TCP gateway that understands the 16-byte frame format
    defined above, one frame per TCP packet (no extra length prefix).
    """

    def __init__(self, host: str, port: int, timeout: Optional[float] = 1.0):
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._sock.setblocking(False)
        self._default_timeout = timeout

    # --- public API ---

    def send(self, msg: can.Message) -> None:
        frame = self._encode_frame(msg)
        self._sock.sendall(frame)

    def recv(self, timeout: Optional[float] = None) -> Optional[can.Message]:
        if timeout is None:
            timeout = self._default_timeout

        rlist, _, _ = select.select([self._sock], [], [], timeout)
        if not rlist:
            return None

        data = self._recv_exact(FRAME_STRUCT.size)
        if not data:
            return None

        return self._decode_frame(data)

    def close(self) -> None:
        try:
            self._sock.close()
        except OSError:
            pass

    # context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # --- internal helpers ---

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

    def _encode_frame(self, msg: can.Message) -> bytes:
        can_id = msg.arbitration_id & 0x1FFFFFFF

        flags = 0
        if msg.is_extended_id:
            flags |= FLAG_EXTENDED
        if getattr(msg, "is_fd", False):
            flags |= FLAG_FD
        if msg.is_remote_frame:
            flags |= FLAG_RTR

        dlc = msg.dlc
        data = (msg.data or b"")[:8].ljust(8, b"\x00")

        return FRAME_STRUCT.pack(can_id, dlc, flags, 0, 0, data)

    def _decode_frame(self, raw: bytes) -> can.Message:
        can_id, dlc, flags, _r1, _r2, data = FRAME_STRUCT.unpack(raw)

        is_extended_id = bool(flags & FLAG_EXTENDED)
        is_fd          = bool(flags & FLAG_FD)
        is_remote      = bool(flags & FLAG_RTR)

        msg = can.Message(
            arbitration_id=can_id,
            is_extended_id=is_extended_id,
            is_fd=is_fd,
            is_remote_frame=is_remote,
            data=data[:dlc],
            dlc=dlc,
        )
        return msg
