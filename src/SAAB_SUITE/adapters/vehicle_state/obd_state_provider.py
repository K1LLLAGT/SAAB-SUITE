"""OBD-II PID-based vehicle state provider."""

from __future__ import annotations

from typing import TYPE_CHECKING

from SAAB_SUITE.kernel.errors import AdapterError
from SAAB_SUITE.ports.vehicle_state import IVehicleStateProvider, VehicleState

if TYPE_CHECKING:
    from SAAB_SUITE.ports.uds import IUdsClient


class ObdStateProvider(IVehicleStateProvider):
    """Reads battery, ignition, engine state via standard PIDs."""

    def __init__(self, uds: IUdsClient) -> None:
        self.uds = uds

    def read(self) -> VehicleState:
        raise AdapterError("OBD state provider not yet implemented")
