"""SPS plan builder -- VIN + cal_id -> ordered FlashPlan."""

from __future__ import annotations

from dataclasses import dataclass

from saab_suite.domain.calibration.identity import CalibrationId
from saab_suite.domain.ecu.module import ModuleKind
from saab_suite.domain.vehicle.profile import VehicleProfile


@dataclass(frozen=True, slots=True)
class FlashStep:
    """A single step in the flash plan."""

    name: str
    timeout_ms: int


@dataclass(frozen=True, slots=True)
class FlashPlan:
    """An ordered, dry-runnable flash plan.

    Constructed only by :func:`build`. Cannot be executed until validated.
    """

    profile: VehicleProfile
    target: ModuleKind
    cal_id: CalibrationId
    steps: tuple[FlashStep, ...]


def build(
    profile: VehicleProfile,
    target: ModuleKind,
    cal_id: CalibrationId,
) -> FlashPlan:
    """Build an ordered FlashPlan."""
    raise NotImplementedError("SPS plan builder not yet implemented")
