"""Pure transformer: (decoded_signal, history_window) -> (display_min, max, units)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True, slots=True)
class AutoScale:
    """Computed display bounds for a signal."""

    display_min: float
    display_max: float
    units: str


def compute(values: Sequence[float], units: str = "") -> AutoScale:
    """Compute display bounds with hysteresis."""
    raise NotImplementedError("autoscale not yet implemented")
