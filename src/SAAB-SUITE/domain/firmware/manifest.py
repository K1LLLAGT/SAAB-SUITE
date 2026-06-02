"""Signed firmware manifest."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from saab_suite.domain.calibration.identity import CalibrationId


@dataclass(frozen=True, slots=True)
class FirmwareManifest:
    """Signed manifest covering a firmware image."""

    cal_id: CalibrationId
    image_size: int
    image_sha256: str
    image_crc32: int
    signed_by: str
    signature: bytes
    issued_at: datetime
