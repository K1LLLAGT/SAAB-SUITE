"""Clock abstraction -- single source of time across the suite."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Protocol

from saab_suite.kernel.types import MonotonicNs, WallUs

UTC = timezone.utc


class Clock(Protocol):
    """Abstract clock. Implemented by SystemClock and MockClock."""

    def monotonic_ns(self) -> MonotonicNs: ...
    def wall_us(self) -> WallUs: ...
    def utc_now(self) -> datetime: ...


class SystemClock:
    """Real clock backed by time.monotonic_ns and the system wall clock."""

    def monotonic_ns(self) -> MonotonicNs:
        return MonotonicNs(time.monotonic_ns())

    def wall_us(self) -> WallUs:
        return WallUs(int(time.time() * 1_000_000))

    def utc_now(self) -> datetime:
        return datetime.now(UTC)


DEFAULT_CLOCK: Clock = SystemClock()
