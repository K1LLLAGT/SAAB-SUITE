"""Vehicle domain -- VIN, profile, platform."""

from SAAB_SUITE.domain.vehicle.platform import (
    BodyStyle,
    Drivetrain,
    EngineCode,
    HaldexGen,
    Market,
    Platform,
    TransmissionCode,
)
from SAAB_SUITE.domain.vehicle.profile import EcuTopology, KnownIssue, VehicleProfile
from SAAB_SUITE.domain.vehicle.vin import Vin

__all__ = [
    "BodyStyle", "Drivetrain", "EcuTopology", "EngineCode", "HaldexGen",
    "KnownIssue", "Market", "Platform", "TransmissionCode", "VehicleProfile", "Vin",
]
