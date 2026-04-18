"""Shared pytest fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture()
def sample_vin_string() -> str:
    """A representative SAAB VIN for the user's 9-3 XWD Aero (synthetic)."""
    return "YS3FD49Y881234567"
