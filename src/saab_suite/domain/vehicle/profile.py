"""VehicleProfile -- the spine of every VIN-aware decision."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from saab_suite.domain.vehicle.platform import (
    BodyStyle,
    Drivetrain,
    EngineCode,
    HaldexGen,
    Market,
    Platform,
    TransmissionCode,
)

if TYPE_CHECKING:
    from saab_suite.domain.ecu.module import ModuleKind
    from saab_suite.domain.vehicle.vin import Vin


class IssueSeverity(StrEnum):
    """Severity of a known issue."""

    INFO = "INFO"
    ADVISORY = "ADVISORY"
    SAFETY = "SAFETY"
    RECALL = "RECALL"


@dataclass(frozen=True, slots=True)
class KnownIssue:
    """A known issue for a VIN range or platform."""

    issue_id: str
    severity: IssueSeverity
    title: str
    description: str
    references: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EcuTopology:
    """Expected ECU/bus topology for a vehicle."""

    expected_modules: frozenset[ModuleKind]
    high_speed_bus_modules: frozenset[ModuleKind]
    medium_speed_bus_modules: frozenset[ModuleKind]
    low_speed_bus_modules: frozenset[ModuleKind] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class VehicleProfile:
    """Aggregate root for a vehicle. Immutable per session."""

    vin: Vin
    platform: Platform
    model_year: int
    market: Market
    body: BodyStyle
    engine: EngineCode
    transmission: TransmissionCode
    drivetrain: Drivetrain
    haldex_generation: HaldexGen | None
    ecu_topology: EcuTopology
    known_issues: tuple[KnownIssue, ...] = ()

    def has_xwd(self) -> bool:
        """True if drivetrain is XWD."""
        return self.drivetrain is Drivetrain.XWD
