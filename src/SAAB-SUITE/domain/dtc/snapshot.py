"""DTC freeze frame / snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.can.signal import DecodedSignal
    from saab_suite.domain.dtc.code import Dtc


@dataclass(frozen=True, slots=True)
class FreezeFrame:
    """Snapshot of vehicle conditions at the time a DTC was set."""

    dtc: Dtc
    signals: tuple[DecodedSignal, ...]
    record_number: int
