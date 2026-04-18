"""CAN frame construction and validation."""

from __future__ import annotations

import pytest

from saab_suite.domain.can.bus import CanBus, CanBusKind
from saab_suite.domain.can.frame import CanFrame, CanId
from saab_suite.kernel.errors import InvalidCanFrameError
from saab_suite.kernel.types import MonotonicNs

HS = CanBus(kind=CanBusKind.HS, name="HS-CAN", bitrate=500000)


def test_dlc_must_match_data_length() -> None:
    with pytest.raises(InvalidCanFrameError):
        CanFrame(MonotonicNs(0), HS, CanId(0x100), False, False, dlc=8, data=b"\x00")


def test_11bit_overflow() -> None:
    with pytest.raises(InvalidCanFrameError):
        CanFrame(MonotonicNs(0), HS, CanId(0x800), False, False, dlc=0, data=b"")


def test_extended_id_ok() -> None:
    f = CanFrame(MonotonicNs(0), HS, CanId(0x18DAF110), True, False, dlc=0, data=b"")
    assert f.is_extended


def test_classic_dlc_max_8() -> None:
    with pytest.raises(InvalidCanFrameError):
        CanFrame(MonotonicNs(0), HS, CanId(0x100), False, False, dlc=9, data=b"\x00" * 9)
