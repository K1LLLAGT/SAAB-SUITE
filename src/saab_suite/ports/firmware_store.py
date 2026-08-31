"""Firmware store port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.domain.calibration.identity import CalibrationId
    from saab_suite.domain.firmware.image import FirmwareImage
    from saab_suite.domain.firmware.manifest import FirmwareManifest


class IFirmwareStore(Protocol):
    """Define the firmware image store interface."""

    def fetch_image(self, cal_id: CalibrationId) -> FirmwareImage:
        """Fetch the firmware image for a calibration."""
        ...

    def fetch_manifest(self, cal_id: CalibrationId) -> FirmwareManifest:
        """Fetch the firmware manifest for a calibration."""
        ...

    def verify_manifest(self, manifest: FirmwareManifest) -> bool:
        """Verify a firmware manifest before use."""
        ...
