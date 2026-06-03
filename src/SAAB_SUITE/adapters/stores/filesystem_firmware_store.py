"""Filesystem-backed firmware store."""

from __future__ import annotations

from typing import TYPE_CHECKING

from SAAB_SUITE.kernel.errors import StoreError
from SAAB_SUITE.ports.firmware_store import IFirmwareStore

if TYPE_CHECKING:
    from pathlib import Path

    from SAAB_SUITE.domain.calibration.identity import CalibrationId
    from SAAB_SUITE.domain.firmware.image import FirmwareImage
    from SAAB_SUITE.domain.firmware.manifest import FirmwareManifest


class FilesystemFirmwareStore(IFirmwareStore):
    """Reads firmware images from ``vendor/firmware/``."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def fetch_image(self, cal_id: CalibrationId) -> FirmwareImage:
        raise StoreError("firmware store not yet implemented")

    def fetch_manifest(self, cal_id: CalibrationId) -> FirmwareManifest:
        raise StoreError("firmware store not yet implemented")

    def verify_manifest(self, manifest: FirmwareManifest) -> bool:
        raise StoreError("firmware store not yet implemented")
