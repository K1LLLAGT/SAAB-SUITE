"""CalibrationId -- partnumber + version + integrity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.ecu.module import ModuleKind
    from saab_suite.domain.vehicle.platform import Market, Platform


@dataclass(frozen=True, slots=True)
class CalibrationId:
    """Canonical identity of a calibration image."""

    part_number: str
    version: str
    market: Market
    platform: Platform
    target_module: ModuleKind
    sha256: str
