"""Vehicle domain -- VIN, profile, platform."""

from saab_suite.domain.vehicle.platform import (
    BodyStyle,
    Drivetrain,
    EngineCode,
    HaldexGen,
    Market,
    Platform,
    TransmissionCode,
)
from saab_suite.domain.vehicle.profile import EcuTopology, KnownIssue, VehicleProfile
from saab_suite.domain.vehicle.vin import Vin

__all__ = [
    "BodyStyle", "Drivetrain", "EcuTopology", "EngineCode", "HaldexGen",
    "KnownIssue", "Market", "Platform", "TransmissionCode", "VehicleProfile", "Vin",
]
