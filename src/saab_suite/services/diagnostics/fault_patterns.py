"""Fault pattern definitions and pluggable matchers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FaultPattern:
    """A fault pattern: a name + an optional matcher."""

    pattern_id: str
    name: str
    description: str
