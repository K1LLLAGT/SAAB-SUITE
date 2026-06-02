"""Boost model -- engine-code-specific turbo characteristics."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.vehicle.profile import VehicleProfile


def predict_boost(profile: VehicleProfile, throttle_pct: float, rpm: int) -> float:
    """Predict steady-state manifold pressure (kPa absolute)."""
    raise NotImplementedError("boost model not yet implemented")
