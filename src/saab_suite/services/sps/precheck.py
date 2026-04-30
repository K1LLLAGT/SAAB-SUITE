"""SPS precheck -- battery, ignition, VIN match, target reachable, audit healthy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.vehicle.profile import VehicleProfile
    from saab_suite.kernel.errors import PrecheckFailed
    from saab_suite.kernel.result import Result
    from saab_suite.ports.audit_log import IAuditLog
    from saab_suite.ports.vehicle_state import IVehicleStateProvider


@dataclass(frozen=True, slots=True)
class PrecheckResult:
    """Aggregate precheck outcome."""

    battery_ok: bool
    ignition_ok: bool
    vin_match: bool
    audit_healthy: bool

    @property
    def all_ok(self) -> bool:
        return self.battery_ok and self.ignition_ok and self.vin_match and self.audit_healthy


def run(
    profile: VehicleProfile,
    state: IVehicleStateProvider,
    audit: IAuditLog,
    min_battery_v: float = 12.4,
) -> Result[PrecheckResult, PrecheckFailed]:
    """Run all precheck steps. Never raises on a failed check; returns Result."""
    raise NotImplementedError("SPS precheck not yet implemented")
