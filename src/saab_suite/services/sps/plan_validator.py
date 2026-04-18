"""SPS plan validator -- interlocks. Produces ValidatedFlashPlan (typed gate)."""

from __future__ import annotations

from dataclasses import dataclass

from saab_suite.domain.vehicle.profile import VehicleProfile
from saab_suite.kernel.errors import InterlockFailure
from saab_suite.kernel.result import Result
from saab_suite.services.sps.plan_builder import FlashPlan


@dataclass(frozen=True, slots=True)
class ValidatedFlashPlan:
    """A FlashPlan that has passed every interlock.

    Constructable only by :func:`validate`. The flash executor accepts only
    this type, so by construction there is no path to execute() that bypasses
    validation.
    """

    plan: FlashPlan
    confirm_token: str


def validate(
    plan: FlashPlan,
    profile: VehicleProfile,
) -> Result[ValidatedFlashPlan, list[InterlockFailure]]:
    """Run all interlocks; return a typed validated plan or a list of failures."""
    raise NotImplementedError("SPS plan validation not yet implemented")
