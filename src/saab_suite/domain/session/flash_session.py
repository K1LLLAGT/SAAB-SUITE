"""FlashSession -- a bounded ECU programming attempt."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from saab_suite.domain.calibration.identity import CalibrationId
    from saab_suite.domain.ecu.module import ModuleKind
    from saab_suite.domain.vehicle.vin import Vin
    from saab_suite.kernel.types import MonotonicNs


class FlashSessionState(StrEnum):
    """Flash session lifecycle state."""

    PENDING = "PENDING"
    PRECHECK = "PRECHECK"
    PLANNING = "PLANNING"
    VALIDATING = "VALIDATING"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETE = "COMPLETE"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class FlashSession:
    """A flash session bound to a vehicle, target module, and calibration."""

    session_id: UUID
    vin: Vin
    target: ModuleKind
    cal_id: CalibrationId
    state: FlashSessionState
    started_at: MonotonicNs
