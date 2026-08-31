"""DTC parsing tests."""

from __future__ import annotations

from saab_suite.domain.dtc.code import Dtc, DtcKind, DtcSystem


def test_dtc_render() -> None:
    d = Dtc(system=DtcSystem.POWERTRAIN, kind=DtcKind.GENERIC, code=0x301)
    assert d.render() == "P0301"


def test_dtc_from_uds_bytes_p0301() -> None:
    # P0301: powertrain (00) + generic (00) + 0x301
    d = Dtc.from_uds_bytes(bytes([0x03, 0x01, 0x00]))
    assert d.system is DtcSystem.POWERTRAIN
    assert d.kind is DtcKind.GENERIC
    assert d.code == 0x301
