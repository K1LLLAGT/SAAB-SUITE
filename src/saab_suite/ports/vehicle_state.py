"""IVehicleStateProvider -- battery, ignition, engine state used by precheck."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class IgnitionState(str, Enum):
    """Ignition switch position."""

    OFF = "OFF"
    ACCESSORY = "ACCESSORY"
    ON = "ON"
    CRANK = "CRANK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class VehicleState:
    """Snapshot of live vehicle state."""

    battery_voltage: float
    ignition: IgnitionState
    engine_running: bool
    coolant_temp_c: float | None = None


class IVehicleStateProvider(Protocol):
    """Provides live vehicle state via OBD/PID reads."""

    def read(self) -> VehicleState: ...
