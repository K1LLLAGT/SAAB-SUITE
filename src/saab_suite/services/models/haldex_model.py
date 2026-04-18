"""Haldex model -- XWD-only. Variant selected by HaldexGen."""

from __future__ import annotations

from saab_suite.domain.vehicle.profile import VehicleProfile


def predict_pump_duty(profile: VehicleProfile, slip_ratio: float, throttle_pct: float) -> float:
    """Predict Haldex pump duty cycle (0..1).

    Raises:
        ValueError: if profile is FWD.
    """
    if not profile.has_xwd():
        msg = "Haldex model requires XWD drivetrain"
        raise ValueError(msg)
    raise NotImplementedError("Haldex model not yet implemented")
