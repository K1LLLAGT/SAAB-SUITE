"""VIN-aware vehicle health report builder."""

from __future__ import annotations

from saab_suite.domain.vehicle.profile import VehicleProfile


def build(profile: VehicleProfile) -> dict[str, object]:
    """Build a structured health report (returned as plain data; UI renders)."""
    raise NotImplementedError("health report not yet implemented")
