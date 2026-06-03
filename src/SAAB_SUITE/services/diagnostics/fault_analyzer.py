"""Fault analyzer -- correlates DTCs across modules into fault patterns."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SAAB_SUITE.domain.dtc.code import Dtc
    from SAAB_SUITE.domain.vehicle.profile import VehicleProfile


def analyze(profile: VehicleProfile, dtcs_by_module: dict[str, list[Dtc]]) -> list[str]:
    """Return a list of fault pattern matches."""
    raise NotImplementedError("fault analysis not yet implemented")
