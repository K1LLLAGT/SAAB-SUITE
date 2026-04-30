"""CAN frame value object."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, NewType

from saab_suite.kernel.errors import InvalidCanFrameError

if TYPE_CHECKING:
    from saab_suite.domain.can.bus import CanBus
    from saab_suite.kernel.types import MonotonicNs

CanId = NewType("CanId", int)


@dataclass(frozen=True, slots=True)
class CanFilter:
    """CAN ID + mask filter."""

    can_id: CanId
    mask: int
    is_extended: bool = False


@dataclass(frozen=True, slots=True)
class CanFrame:
    """A single CAN frame as observed on a bus.

    Validated at construction:
        - DLC matches len(data)
        - 11-bit IDs <= 0x7FF; 29-bit IDs <= 0x1FFFFFFF
        - data length <= 8 (classic) or <= 64 (FD)
    """

    timestamp: MonotonicNs
    bus: CanBus
    can_id: CanId
    is_extended: bool
    is_fd: bool
    dlc: int
    data: bytes

    def __post_init__(self) -> None:
        if self.dlc != len(self.data):
            msg = f"DLC {self.dlc} does not match data length {len(self.data)}"
            raise InvalidCanFrameError(msg)
        if not self.is_extended and self.can_id > 0x7FF:
            msg = f"11-bit ID overflow: 0x{self.can_id:X}"
            raise InvalidCanFrameError(msg)
        if self.is_extended and self.can_id > 0x1FFFFFFF:
            msg = f"29-bit ID overflow: 0x{self.can_id:X}"
            raise InvalidCanFrameError(msg)
        max_dlc = 64 if self.is_fd else 8
        if self.dlc > max_dlc:
            msg = f"DLC {self.dlc} exceeds {max_dlc} (FD={self.is_fd})"
            raise InvalidCanFrameError(msg)
