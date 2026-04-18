"""Filesystem-backed firmware store."""

from __future__ import annotations

from pathlib import Path

from saab_suite.domain.calibration.identity import CalibrationId
from saab_suite.domain.firmware.image import FirmwareImage
from saab_suite.domain.firmware.manifest import FirmwareManifest
from saab_suite.kernel.errors import StoreError
from saab_suite.ports.firmware_store import IFirmwareStore


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
