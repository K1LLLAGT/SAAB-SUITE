"""VIN value-object tests."""

from __future__ import annotations

import pytest

from saab_suite.domain.vehicle.vin import Vin
from saab_suite.kernel.errors import InvalidVinError


def test_vin_uppercases() -> None:
    v = Vin("ys3fd49y881234567")
    assert v == "YS3FD49Y881234567"


def test_vin_length_must_be_17() -> None:
    with pytest.raises(InvalidVinError):
        Vin("TOO_SHORT")


def test_vin_rejects_i_o_q() -> None:
    with pytest.raises(InvalidVinError):
        Vin("YS3FD49Y8812345I7")


def test_vin_sections() -> None:
    v = Vin("YS3FD49Y881234567")
    assert v.wmi == "YS3"
    assert v.vds == "FD49Y8"
    assert v.vis == "81234567"
    assert v.model_year_char == "8"
    assert v.check_digit == "8"
