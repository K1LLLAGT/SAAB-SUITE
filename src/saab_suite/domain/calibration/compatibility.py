"""Calibration to vehicle compatibility rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.calibration.identity import CalibrationId
    from saab_suite.domain.vehicle.profile import VehicleProfile


@dataclass(frozen=True, slots=True)
class CompatibilityRule:
    """A single compatibility constraint between a calibration and a profile."""

    rule_id: str
    description: str

    def applies(self, cal: CalibrationId, profile: VehicleProfile) -> bool:
        """Return True if this rule is relevant; subclasses override."""
        raise NotImplementedError

    def is_satisfied(self, cal: CalibrationId, profile: VehicleProfile) -> bool:
        """Return True if the rule passes for this (cal, profile) pair."""
        raise NotImplementedError
