"""Mock vehicle state provider for tests."""

from __future__ import annotations

from saab_suite.ports.vehicle_state import IgnitionState, IVehicleStateProvider, VehicleState


class MockStateProvider(IVehicleStateProvider):
    """Returns a fixed VehicleState. Configurable per-test."""

    def __init__(self, state: VehicleState | None = None) -> None:
        self._state = state or VehicleState(
            battery_voltage=12.6,
            ignition=IgnitionState.ON,
            engine_running=False,
        )

    def read(self) -> VehicleState:
        return self._state
