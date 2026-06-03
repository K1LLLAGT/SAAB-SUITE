"""VIN-aware vehicle health report builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SAAB_SUITE.domain.vehicle.profile import VehicleProfile


def build(profile: VehicleProfile) -> dict[str, object]:
    """Build a structured health report (returned as plain data; UI renders)."""
    raise NotImplementedError("health report not yet implemented")
