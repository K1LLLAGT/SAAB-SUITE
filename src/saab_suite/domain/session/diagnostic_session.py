"""DiagnosticSession -- a bounded interaction with one or more modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from saab_suite.domain.vehicle.profile import VehicleProfile
    from saab_suite.kernel.types import MonotonicNs


@dataclass(frozen=True, slots=True)
class DiagnosticSession:
    """A diagnostic session bound to a vehicle and a wall window."""

    session_id: UUID
    profile: VehicleProfile
    started_at: MonotonicNs
