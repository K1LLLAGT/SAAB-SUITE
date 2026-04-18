"""OBD-II PID-based vehicle state provider."""

from __future__ import annotations

from saab_suite.kernel.errors import AdapterError
from saab_suite.ports.uds import IUdsClient
from saab_suite.ports.vehicle_state import IVehicleStateProvider, VehicleState


class ObdStateProvider(IVehicleStateProvider):
    """Reads battery, ignition, engine state via standard PIDs."""

    def __init__(self, uds: IUdsClient) -> None:
        self.uds = uds

    def read(self) -> VehicleState:
        raise AdapterError("OBD state provider not yet implemented")
