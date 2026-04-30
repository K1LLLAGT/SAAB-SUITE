"""ECU module identity."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.ecu.address import CanAddressPair


class ModuleKind(StrEnum):
    """Canonical ECU module kinds across SAAB 9-3 / 9-5."""

    ECM = "ECM"
    TCM = "TCM"
    BCM = "BCM"
    ABS = "ABS"
    SRS = "SRS"
    EHU = "EHU"
    HVAC = "HVAC"
    XWD = "XWD"
    EPS = "EPS"
    PSCM = "PSCM"
    SDM = "SDM"
    DLC = "DLC"
    CIM = "CIM"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class Module:
    """An ECU module instance with addressing and identity."""

    kind: ModuleKind
    name: str
    can_addresses: CanAddressPair
    description: str = ""
