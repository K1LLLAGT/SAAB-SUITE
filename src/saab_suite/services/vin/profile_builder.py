"""Profile builder -- DecodedVin + platform rules -> VehicleProfile."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.vehicle.profile import VehicleProfile
    from saab_suite.domain.vehicle.vin import Vin


def build(vin: Vin) -> VehicleProfile:
    """Build a VehicleProfile from a VIN by consulting the platform rules."""
    raise NotImplementedError("VIN profile builder not yet implemented")
