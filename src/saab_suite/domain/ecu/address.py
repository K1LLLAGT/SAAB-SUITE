"""ECU addressing -- CAN, UDS, KWP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.can.frame import CanId


@dataclass(frozen=True, slots=True)
class CanAddressPair:
    """A pair of CAN IDs for diagnostic request/response (ISO-TP)."""

    request: CanId
    response: CanId


@dataclass(frozen=True, slots=True)
class UdsAddress:
    """UDS logical address (often equal to CAN response ID)."""

    value: int


@dataclass(frozen=True, slots=True)
class KwpAddress:
    """KWP2000 8-bit logical address."""

    value: int

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 0xFF:
            msg = f"KWP address out of range: 0x{self.value:X}"
            raise ValueError(msg)
