"""SPS precheck -- battery, ignition, VIN match, target reachable, audit healthy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SAAB_SUITE.domain.vehicle.profile import VehicleProfile
    from SAAB_SUITE.kernel.errors import PrecheckFailed
    from SAAB_SUITE.kernel.result import Result
    from SAAB_SUITE.ports.audit_log import IAuditLog
    from SAAB_SUITE.ports.vehicle_state import IVehicleStateProvider


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
