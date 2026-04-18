"""GDS2 deliverable metadata."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from saab_suite.domain.calibration.identity import CalibrationId


class DeliverableSource(str, Enum):
    """Origin of a deliverable."""

    GDS2_GLOBAL = "GDS2_GLOBAL"
    GDS2_CHINA = "GDS2_CHINA"
    GDS2_NAO = "GDS2_NAO"
    OPEL_VAUXHALL = "OPEL_VAUXHALL"
    SAAB = "SAAB"
    VINFAST = "VINFAST"
    CUSTOM = "CUSTOM"


@dataclass(frozen=True, slots=True)
class Deliverable:
    """GDS2 deliverable: a packaged calibration with manifest."""

    cal_id: CalibrationId
    source: DeliverableSource
    issued_at: datetime
    xml_path: str
    archive_path: str
