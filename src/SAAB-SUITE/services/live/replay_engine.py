"""Replay an NDJSON CAN log as an ICanSource."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from saab_suite.ports.can_source import ICanSource


def from_file(path: Path, speed: float = 1.0) -> ICanSource:
    """Wrap a CAN log file as an ICanSource."""
    raise NotImplementedError("replay engine not yet implemented")
