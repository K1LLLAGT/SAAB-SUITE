#!/data/data/com.termux/files/usr/bin/bash
# ============================================================================
# rebuild_saab_suite.sh
# Applies the ports-aligned CAN/UDS rebuild to the SAAB-SUITE project at
#   /sdcard/Download/SAAB-SUITE   (Termux / Android)
#
# Behaviour:
#   * If the project is missing, clones it (on ext4 first, then copies to /sdcard,
#     because git on /sdcard's FUSE filesystem is unreliable). The repo is private,
#     so set GH_TOKEN if a clone is needed.
#   * If the project is already present, it is LEFT AS-IS (no clone, no clobber)
#     and only the updated files below are written.
#   * Every replaced file is backed up under .saab_rebuild_backup_<timestamp>/.
#   * File CONTENTS are embedded here, so this script is self-contained and
#     reproducible regardless of what is already on disk.
#
# Options (env vars):
#   FRESH=1     re-clone from GitHub even if the project exists (after backup)
#   GH_TOKEN=.. GitHub token used for the clone of the private repo
# ============================================================================
set -euo pipefail

REPO_URL="https://github.com/K1LLLAGT/SAAB-SUITE.git"
DEST="/sdcard/Download/SAAB-SUITE"
PKG="src/saab_suite"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP="$DEST/.saab_rebuild_backup_$TS"
FRESH="${FRESH:-0}"
GH_TOKEN="${GH_TOKEN:-}"

echo "==> SAAB-SUITE rebuild"
echo "    target : $DEST"

# 0. storage access ----------------------------------------------------------
if [ ! -d /sdcard ]; then
  echo "!! /sdcard not accessible. Run:  termux-setup-storage   then re-run." >&2
  exit 1
fi

# 1. ensure the project is present -------------------------------------------
do_clone() {
  local url="$REPO_URL"
  [ -n "$GH_TOKEN" ] && url="https://${GH_TOKEN}@github.com/K1LLLAGT/SAAB-SUITE.git"
  local tmp="$HOME/.saab_clone_$TS"
  rm -rf "$tmp"
  if git clone --depth 1 "$url" "$tmp"; then
    rm -rf "$DEST"; mkdir -p "$DEST"; cp -a "$tmp/." "$DEST/"; rm -rf "$tmp"
    echo "    cloned into $DEST"
  else
    rm -rf "$tmp"
    echo "!! clone failed. The repo is private; provide a token, e.g.:" >&2
    echo "     GH_TOKEN=ghp_xxx bash $0" >&2
    echo "   or create $DEST manually and re-run." >&2
    exit 1
  fi
}

if [ "$FRESH" = "1" ]; then
  echo "==> FRESH=1 -> re-cloning from GitHub"
  [ -d "$DEST" ] && { mkdir -p "$BACKUP"; cp -a "$DEST/." "$BACKUP/" 2>/dev/null || true; echo "    backed up old tree to $BACKUP"; }
  do_clone
elif [ ! -d "$DEST" ]; then
  echo "==> project missing -> cloning"
  do_clone
else
  echo "==> project found -> keeping existing files (no clone)"
fi

mkdir -p "$BACKUP"

# 2. writers -----------------------------------------------------------------
put() {                       # back up (if present) then overwrite from stdin
  local rel="$1" full="$DEST/$1"
  mkdir -p "$(dirname "$full")"
  if [ -f "$full" ]; then mkdir -p "$BACKUP/$(dirname "$rel")"; cp -a "$full" "$BACKUP/$rel"; fi
  cat > "$full"
  echo "    wrote $rel"
}
put_if_absent() {             # create only if missing (don't clobber __init__ exports)
  local rel="$1" full="$DEST/$1"
  if [ -f "$full" ]; then echo "    kept  $rel (exists - verify it exports the new class)"; cat >/dev/null; return 0; fi
  mkdir -p "$(dirname "$full")"; cat > "$full"; echo "    wrote $rel"
}

echo "==> writing updated modules (backups -> $BACKUP)"
put "src/saab_suite/adapters/isotp/transport.py" << 'SAAB_EOF'
"""IsoTpTransport -- ISO 15765-2 over an ICanSource + ICanSink pair.

Implements ports.isotp.IIsoTpTransport. Owns all ISO-TP framing (SF / FF / CF /
flow control); callers exchange raw UDS service payloads (WirePayload).

Block size and STmin in the flow-control frame we emit are 0 (the peer may send
all consecutive frames back-to-back), which is fine for diagnostic traffic.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable, cast

from saab_suite.domain.can.frame import CanFrame, CanFilter, CanId
from saab_suite.kernel.errors import IsoTpError

if TYPE_CHECKING:
    from saab_suite.domain.can.bus import CanBus
    from saab_suite.domain.ecu.address import CanAddressPair
    from saab_suite.kernel.types import MonotonicNs, WirePayload
    from saab_suite.ports.can_sink import ICanSink
    from saab_suite.ports.can_source import ICanSource

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
SAAB_EOF

put "src/saab_suite/adapters/uds/client.py" << 'SAAB_EOF'
"""UdsClient -- ISO 14229 client over an IIsoTpTransport.

Implements ports.uds.IUdsClient. Each method builds a request payload, sends it
through the ISO-TP transport, and returns the raw response WirePayload. Negative
responses (0x7F ...) are returned as-is for the caller to interpret, EXCEPT the
"response pending" NRC 0x78, which is transparently waited out.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from saab_suite.kernel.types import WirePayload
    from saab_suite.ports.isotp import IIsoTpTransport

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
SAAB_EOF

put "src/saab_suite/adapters/can/pycan_backend.py" << 'SAAB_EOF'
"""PyCanBackend -- python-can backend implementing both ICanSource and ICanSink.

python-can already speaks SocketCAN *and* SLCAN/CANUSB (and pcan, etc.) via its
`interface` selector, so this single class realizes both the socketcan_source
and canusb_source Phase-2 stubs. Pick the concrete transport via runtime config.
J2534 is NOT python-can; that stays a separate backend over IJ2534Device.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable, Iterator, Optional, cast

from saab_suite.domain.can.frame import CanFrame, CanId
from saab_suite.ports.can_source import CanSourceStats

try:
    import can
except ImportError:
    can = None

if TYPE_CHECKING:
    from saab_suite.domain.can.bus import CanBus
    from saab_suite.domain.can.frame import CanFilter
    from saab_suite.kernel.types import MonotonicNs


class PyCanBackend:
    """Implements ICanSource + ICanSink over python-can."""

    def __init__(self, channel: str, interface: str, clock: Callable[[], int] = time.monotonic_ns) -> None:
        self._channel = channel
        self._interface = interface
        self._clock = clock
        self._bus_obj: Optional["can.BusABC"] = None
        self._bus: Optional["CanBus"] = None
        self._frames_read = 0
        self._bytes_read = 0

    # -- lifecycle (ICanSource) -----------------------------------------------
    def open(self, bus: "CanBus", bitrate: int) -> None:
        if can is None:
            raise RuntimeError("python-can not installed. Install saab-suite[hardware].")
        self._bus = bus
        self._bus_obj = can.Bus(channel=self._channel, interface=self._interface, bitrate=bitrate)

    def close(self) -> None:
        if self._bus_obj is not None:
            self._bus_obj.shutdown()
            self._bus_obj = None

    # -- read side (ICanSource) -----------------------------------------------
    def read(self, timeout_ms: int) -> Optional[CanFrame]:
        if self._bus_obj is None or self._bus is None:
            raise RuntimeError("backend not open")
        msg = self._bus_obj.recv(timeout_ms / 1000.0)
        if msg is None:
            return None
        data = bytes(msg.data)
        self._frames_read += 1
        self._bytes_read += len(data)
        return CanFrame(
            timestamp=cast("MonotonicNs", self._clock()),
            bus=self._bus,
            can_id=cast(CanId, msg.arbitration_id),
            is_extended=bool(msg.is_extended_id),
            is_fd=bool(getattr(msg, "is_fd", False)),
            dlc=len(data),
            data=data,
        )

    def iter_frames(self) -> Iterator[CanFrame]:
        while True:
            frame = self.read(timeout_ms=100)
            if frame is not None:
                yield frame

    def filter(self, mask: "CanFilter") -> None:
        if self._bus_obj is None:
            raise RuntimeError("backend not open")
        self._bus_obj.set_filters(
            [{"can_id": int(mask.can_id), "can_mask": mask.mask, "extended": mask.is_extended}]
        )

    @property
    def stats(self) -> CanSourceStats:
        return CanSourceStats(
            frames_read=self._frames_read, bytes_read=self._bytes_read, bus_errors=0, overruns=0
        )

    # -- write side (ICanSink) ------------------------------------------------
    def write(self, frame: CanFrame) -> None:
        if self._bus_obj is None:
            raise RuntimeError("backend not open")
        self._bus_obj.send(
            can.Message(
                arbitration_id=int(frame.can_id),
                data=frame.data,
                is_extended_id=frame.is_extended,
                is_fd=frame.is_fd,
            )
        )

    def flush(self) -> None:
        if self._bus_obj is not None:
            self._bus_obj.flush_tx_buffer()
SAAB_EOF

put_if_absent "src/saab_suite/adapters/isotp/__init__.py" << 'SAAB_EOF'
from saab_suite.adapters.isotp.transport import IsoTpTransport

__all__ = ["IsoTpTransport"]
SAAB_EOF

put_if_absent "src/saab_suite/adapters/uds/__init__.py" << 'SAAB_EOF'
from saab_suite.adapters.uds.client import UdsClient

__all__ = ["UdsClient"]
SAAB_EOF

# 3. remove cruft ------------------------------------------------------------
echo "==> cleaning cruft"
find "$DEST/$PKG/adapters/can" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
rm -f "$DEST/$PKG/adapters/can/remote_interface.py.bak" \
      "$DEST/$PKG/adapters/can/remote_interface.py.bak.bak" 2>/dev/null || true

# 4. OPTIONAL legacy retirement ---------------------------------------------
#    Do this ONLY after cutting imports over to the new adapters/uds/client.py.
#    Uncomment to delete the legacy stack:
# rm -f "$DEST/$PKG/adapters/can/interface.py" \
#       "$DEST/$PKG/adapters/can/remote_interface.py"
# echo "    removed legacy interface.py / remote_interface.py"

# 5. syntax check (compiles to a temp .pyc on ext4, never to /sdcard) --------
if command -v python >/dev/null 2>&1; then
  echo "==> byte-compiling updated files"
  python - "$DEST/$PKG" << 'PYEOF'
import os, sys, tempfile, py_compile, pathlib
root = pathlib.Path(sys.argv[1])
ok = True
for rel in ("adapters/isotp/transport.py","adapters/uds/client.py","adapters/can/pycan_backend.py"):
    p = root / rel
    fd, tmp = tempfile.mkstemp(suffix=".pyc"); os.close(fd)
    try:
        py_compile.compile(str(p), cfile=tmp, doraise=True)
        print("    ok  ", rel)
    except Exception as e:
        ok = False; print("    FAIL", rel, "->", e)
    finally:
        try: os.remove(tmp)
        except OSError: pass
sys.exit(0 if ok else 1)
PYEOF
fi

echo
echo "==> done."
echo "    applied to : $DEST"
echo "    backup     : $BACKUP   (replaced files; delete when satisfied)"
echo
echo "Next: point the legacy UDS caller at the new client, then optionally"
echo "uncomment the legacy-retirement block above and re-run."
