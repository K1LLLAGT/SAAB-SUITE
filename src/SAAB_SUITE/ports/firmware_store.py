"""IFirmwareStore -- firmware image persistence."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from SAAB_SUITE.domain.calibration.identity import CalibrationId
    from SAAB_SUITE.domain.firmware.image import FirmwareImage
    from SAAB_SUITE.domain.firmware.manifest import FirmwareManifest


class IFirmwareStore(Protocol):
    """Firmware image storage with signed manifests."""

    def fetch_image(self, cal_id: CalibrationId) -> FirmwareImage: ...
    def fetch_manifest(self, cal_id: CalibrationId) -> FirmwareManifest: ...
    def verify_manifest(self, manifest: FirmwareManifest) -> bool: ...
