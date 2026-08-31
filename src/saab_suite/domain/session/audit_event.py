"""AuditEvent -- append-only, hash-chained record of vehicle-touching actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    from saab_suite.domain.vehicle.vin import Vin
    from saab_suite.kernel.types import MonotonicNs


class AuditAction(StrEnum):
    """Auditable actions."""

    SESSION_OPEN = "SESSION_OPEN"
    SESSION_CLOSE = "SESSION_CLOSE"
    DTC_READ = "DTC_READ"
    DTC_CLEAR = "DTC_CLEAR"
    MODULE_DISCOVER = "MODULE_DISCOVER"
    SPS_PRECHECK = "SPS_PRECHECK"
    SPS_PLAN_BUILD = "SPS_PLAN_BUILD"
    SPS_PLAN_VALIDATE = "SPS_PLAN_VALIDATE"
    SPS_FLASH_BEGIN = "SPS_FLASH_BEGIN"
    SPS_FLASH_BLOCK = "SPS_FLASH_BLOCK"
    SPS_FLASH_VERIFY = "SPS_FLASH_VERIFY"
    SPS_FLASH_COMPLETE = "SPS_FLASH_COMPLETE"
    SPS_FLASH_ABORT = "SPS_FLASH_ABORT"
    SPS_RECOVERY = "SPS_RECOVERY"


class AuditResult(StrEnum):
    """Outcome of an audited action."""

    OK = "OK"
    FAIL = "FAIL"
    ABORTED = "ABORTED"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """A single auditable event. Forms a hash chain when persisted."""

    event_id: UUID
    monotonic_ns: MonotonicNs
    wall_utc: datetime
    actor: str
    vin: Vin | None
    action: AuditAction
    target: str
    result: AuditResult
    correlation_id: UUID
    parameters: dict[str, Any] = field(default_factory=dict)
    prev_hash: str = ""
    hash: str = ""
