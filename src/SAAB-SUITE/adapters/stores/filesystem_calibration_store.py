"""Filesystem-backed calibration store."""

from __future__ import annotations

from typing import TYPE_CHECKING

from saab_suite.kernel.errors import StoreError
from saab_suite.ports.calibration_store import ICalibrationStore

if TYPE_CHECKING:
    from pathlib import Path

    from saab_suite.domain.calibration.identity import CalibrationId
    from saab_suite.domain.vehicle.profile import VehicleProfile


class FilesystemCalibrationStore(ICalibrationStore):
    """Reads calibration metadata from ``vendor/deliverables/``."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def get(self, cal_id: CalibrationId) -> CalibrationId | None:
        raise StoreError("calibration store not yet implemented")

    def candidates(self, profile: VehicleProfile) -> list[CalibrationId]:
        raise StoreError("calibration store not yet implemented")

    def all(self) -> list[CalibrationId]:
        raise StoreError("calibration store not yet implemented")
