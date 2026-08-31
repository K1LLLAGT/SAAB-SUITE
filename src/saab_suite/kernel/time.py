"""Clock abstractions shared across the suite."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Protocol

from saab_suite.kernel.types import MonotonicNs, WallUs


class Clock(Protocol):
    """Define the clock interface used by runtime components."""

    def monotonic_ns(self) -> MonotonicNs:
        """Return the current monotonic time in nanoseconds."""
        ...

    def wall_us(self) -> WallUs:
        """Return the current wall-clock time in microseconds."""
        ...

    def utc_now(self) -> datetime:
        """Return the current UTC time."""
        ...


class SystemClock:
    """Provide clock values from the host system."""

    def monotonic_ns(self) -> MonotonicNs:
        """Return the current monotonic time in nanoseconds."""
        return MonotonicNs(time.monotonic_ns())

    def wall_us(self) -> WallUs:
        """Return the current wall-clock time in microseconds."""
        return WallUs(int(time.time() * 1_000_000))

    def utc_now(self) -> datetime:
        """Return the current UTC time."""
        return datetime.now(UTC)


DEFAULT_CLOCK: Clock = SystemClock()
