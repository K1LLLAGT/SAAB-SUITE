"""VIN decoder -- VIN -> structured fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.vehicle.platform import Market, Platform
    from saab_suite.domain.vehicle.vin import Vin


@dataclass(frozen=True, slots=True)
class DecodedVin:
    """Structured VIN fields as decoded from the 17 characters."""

    vin: Vin
    wmi: str
    model_year: int
    market: Market
    platform: Platform


def decode(vin: Vin) -> DecodedVin:
    """Decode the VIN into structured fields."""
    raise NotImplementedError("VIN decode not yet implemented")
