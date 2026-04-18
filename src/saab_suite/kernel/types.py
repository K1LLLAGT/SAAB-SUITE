"""Type aliases used across the kernel boundary."""

from __future__ import annotations

from typing import NewType, TypeAlias

MonotonicNs = NewType("MonotonicNs", int)
WallUs = NewType("WallUs", int)
WirePayload: TypeAlias = bytes
