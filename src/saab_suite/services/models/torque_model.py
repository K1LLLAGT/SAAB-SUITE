"""Torque model -- engine + transmission combined limits."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.vehicle.profile import VehicleProfile


def max_safe_torque_nm(profile: VehicleProfile, rpm: int) -> float:
    """Return the maximum torque (Nm) safe for the engine + trans combo.

    For the user's B284R + AF40-6 combo, the AF40-6 input torque rating is
    the binding constraint above ~3500 RPM.
    """
    raise NotImplementedError("torque model not yet implemented")
