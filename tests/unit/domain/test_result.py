"""Result type smoke tests."""

from __future__ import annotations

import pytest

from saab_suite.kernel.result import Err, Ok


def test_ok_unwrap() -> None:
    assert Ok(42).unwrap() == 42


def test_err_unwrap_raises() -> None:
    with pytest.raises(ValueError):
        Err("boom").unwrap()


def test_is_ok_is_err() -> None:
    assert Ok(1).is_ok() and not Ok(1).is_err()
    assert Err(1).is_err() and not Err(1).is_ok()
