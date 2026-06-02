"""ICalibrationStore -- calibration metadata persistence."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.domain.calibration.identity import CalibrationId
    from saab_suite.domain.vehicle.profile import VehicleProfile


class ICalibrationStore(Protocol):
    """Calibration metadata storage."""

    def get(self, cal_id: CalibrationId) -> CalibrationId | None: ...
    def candidates(self, profile: VehicleProfile) -> list[CalibrationId]: ...
    def all(self) -> list[CalibrationId]: ...
