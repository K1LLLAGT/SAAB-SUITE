"""CAN bus identity."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CanBusKind(str, Enum):
    """Bus classification."""

    HS = "HS"
    MS = "MS"
    LS = "LS"
    GMLAN_HS = "GMLAN_HS"
    GMLAN_MS = "GMLAN_MS"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class CanBus:
    """A named CAN bus."""

    kind: CanBusKind
    name: str
    bitrate: int
