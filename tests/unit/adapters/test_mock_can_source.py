"""MockCanSource behaves correctly."""

from __future__ import annotations

from SAAB_SUITE.adapters.can.mock_source import MockCanSource
from SAAB_SUITE.domain.can.bus import CanBus, CanBusKind
from SAAB_SUITE.domain.can.frame import CanFrame, CanId
from SAAB_SUITE.kernel.types import MonotonicNs

HS = CanBus(kind=CanBusKind.HS, name="HS-CAN", bitrate=500000)


def test_returns_none_when_empty() -> None:
    src = MockCanSource()
    src.open(HS, 500000)
    assert src.read(timeout_ms=10) is None


def test_yields_scripted_frames() -> None:
    f = CanFrame(MonotonicNs(0), HS, CanId(0x100), False, False, dlc=0, data=b"")
    src = MockCanSource(frames=[f])
    src.open(HS, 500000)
    out = src.read(timeout_ms=10)
    assert out is f
    assert src.stats.frames_read == 1
