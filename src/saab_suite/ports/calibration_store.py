"""Calibration store port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.domain.calibration.identity import CalibrationId
    from saab_suite.domain.vehicle.profile import VehicleProfile


class ICalibrationStore(Protocol):
    """Define the calibration metadata store interface."""

    def get(self, cal_id: CalibrationId) -> CalibrationId | None:
        """Return a calibration by identifier when available."""
        ...

    def candidates(self, profile: VehicleProfile) -> list[CalibrationId]:
        """Return compatible calibrations for a vehicle profile."""
        ...

    def all(self) -> list[CalibrationId]:
        """Return all known calibrations."""
        ...
