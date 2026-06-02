"""Module discovery service."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.ecu.module import Module
    from saab_suite.domain.ecu.registry import ModuleRegistry
    from saab_suite.domain.vehicle.profile import VehicleProfile
    from saab_suite.ports.uds import IUdsClient


def discover_modules(
    profile: VehicleProfile,
    registry: ModuleRegistry,
    uds: IUdsClient,
    timeout_ms: int = 1000,
) -> list[Module]:
    """Probe expected modules; return responders."""
    raise NotImplementedError("module discovery not yet implemented")
