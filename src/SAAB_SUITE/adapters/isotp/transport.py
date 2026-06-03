"""IsoTpTransport -- ISO 15765-2 over an ICanSource + ICanSink pair.

Implements ports.isotp.IIsoTpTransport. Owns all ISO-TP framing (SF / FF / CF /
flow control); callers exchange raw UDS service payloads (WirePayload).

Block size and STmin in the flow-control frame we emit are 0 (the peer may send
all consecutive frames back-to-back), which is fine for diagnostic traffic.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable, cast

from SAAB_SUITE.domain.can.frame import CanFrame, CanFilter, CanId
from SAAB_SUITE.kernel.errors import IsoTpError

if TYPE_CHECKING:
    from SAAB_SUITE.domain.can.bus import CanBus
    from SAAB_SUITE.domain.ecu.address import CanAddressPair
    from SAAB_SUITE.kernel.types import MonotonicNs, WirePayload
    from SAAB_SUITE.ports.can_sink import ICanSink
    from SAAB_SUITE.ports.can_source import ICanSource

_SF, _FF, _CF, _FC = 0x0, 0x1, 0x2, 0x3
_FC_CTS = 0x0
_STD_MASK = 0x7FF
_EXT_MASK = 0x1FFFFFFF


def _pad8(data: bytes) -> bytes:
    return data + b"\x00" * (8 - len(data))


class IsoTpTransport:
    """ISO-TP transport. Construct with an opened source+sink and the bus they
    run on; call open() with the ECU address pair before send/recv."""

    def __init__(
        self,
        source: "ICanSource",
        sink: "ICanSink",
        bus: "CanBus",
        clock: Callable[[], int] = time.monotonic_ns,
    ) -> None:
        self._source = source
        self._sink = sink
        self._bus = bus
        self._clock = clock
        self._tx: int = 0
        self._rx: int = 0
        self._ext: bool = False

    def open(self, addresses: "CanAddressPair") -> None:
        # CanAddressPair carries bare CanId request/response (no per-address
        # extended flag), so frame format is inferred from ID width: 11-bit OBD
        # IDs (<= 0x7FF, e.g. 0x7E0/0x7E8) are standard; 29-bit GMLAN diagnostic
        # IDs (e.g. 0x18DAxxxx) are extended. Make this explicit later only if
        # you ever need an 11-bit-range ID sent as an extended frame.
        self._tx = int(addresses.request)
        self._rx = int(addresses.response)
        self._ext = self._tx > _STD_MASK
        mask = _EXT_MASK if self._ext else _STD_MASK
        self._source.filter(CanFilter(can_id=cast(CanId, self._rx), mask=mask, is_extended=self._ext))

    def close(self) -> None:
        self._source.close()

    # --- sending --------------------------------------------------------------
    def send(self, payload: "WirePayload", timeout_ms: int) -> None:
        p = bytes(payload)
        if len(p) <= 7:
            self._sink.write(self._mk(_pad8(bytes([(_SF << 4) | len(p)]) + p)))
        else:
            total = len(p)
            ff = bytes([(_FF << 4) | (total >> 8), total & 0xFF]) + p[:6]
            self._sink.write(self._mk(_pad8(ff)))
            fc = self._await(timeout_ms)
            if (fc.data[0] >> 4) != _FC or (fc.data[0] & 0x0F) != _FC_CTS:
                raise IsoTpError("expected flow-control Clear-To-Send after first frame")
            seq, off = 1, 6
            while off < total:
                cf = bytes([(_CF << 4) | (seq & 0x0F)]) + p[off : off + 7]
                self._sink.write(self._mk(_pad8(cf)))
                off += 7
                seq += 1
        self._sink.flush()

    # --- receiving ------------------------------------------------------------
    def recv(self, timeout_ms: int) -> "WirePayload":
        first = self._await(timeout_ms)
        pci = first.data[0] >> 4
        if pci == _SF:
            n = first.data[0] & 0x0F
            return cast("WirePayload", bytes(first.data[1 : 1 + n]))
        if pci == _FF:
            total = ((first.data[0] & 0x0F) << 8) | first.data[1]
            buf = bytearray(first.data[2:8])
            self._sink.write(self._mk(_pad8(bytes([(_FC << 4) | _FC_CTS, 0x00, 0x00]))))
            self._sink.flush()
            expected = 1
            while len(buf) < total:
                cf = self._await(timeout_ms)
                if (cf.data[0] >> 4) != _CF:
                    continue
                if (cf.data[0] & 0x0F) != (expected & 0x0F):
                    raise IsoTpError(f"out-of-order CF: {cf.data[0] & 0x0F} != {expected & 0x0F}")
                buf.extend(cf.data[1:8])
                expected += 1
            return cast("WirePayload", bytes(buf[:total]))
        raise IsoTpError(f"unexpected ISO-TP PCI on first frame: 0x{pci:X}")

    # --- helpers --------------------------------------------------------------
    def _mk(self, data8: bytes) -> CanFrame:
        return CanFrame(
            timestamp=cast("MonotonicNs", self._clock()),
            bus=self._bus,
            can_id=cast(CanId, self._tx),
            is_extended=self._ext,
            is_fd=False,
            dlc=len(data8),
            data=data8,
        )

    def _await(self, timeout_ms: int) -> CanFrame:
        deadline = time.monotonic() + timeout_ms / 1000.0
        while time.monotonic() < deadline:
            frame = self._source.read(timeout_ms=20)
            if frame is None or int(frame.can_id) != self._rx:
                continue
            return frame
        raise IsoTpError("ISO-TP receive timed out")
