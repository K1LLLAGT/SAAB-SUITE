"""CAN signal descriptors and decoded values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.can.frame import CanId
    from saab_suite.kernel.types import MonotonicNs


@dataclass(frozen=True, slots=True)
class SignalDescriptor:
    """Static signal definition extracted from a DBC."""

    name: str
    can_id: CanId
    start_bit: int
    length: int
    is_signed: bool
    is_little_endian: bool
    factor: float
    offset: float
    unit: str
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True, slots=True)
class DecodedSignal:
    """A decoded signal value with timestamp."""

    descriptor: SignalDescriptor
    value: float
    timestamp: MonotonicNs
