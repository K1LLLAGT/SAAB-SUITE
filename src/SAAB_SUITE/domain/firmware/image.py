"""FirmwareImage -- bytes + metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SAAB_SUITE.domain.calibration.identity import CalibrationId


@dataclass(frozen=True, slots=True)
class FirmwareImage:
    """A firmware image with calibration identity."""

    cal_id: CalibrationId
    payload: bytes
    block_size: int = 0x1000
