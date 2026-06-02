"""Backpressured pipeline: Source -> Filter -> Decode -> Autoscale -> Sinks[]."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from saab_suite.domain.can.signal import DecodedSignal
    from saab_suite.ports.can_source import ICanSource


def stream(source: ICanSource, signals: Iterable[str]) -> Iterable[DecodedSignal]:
    """Stream decoded signals from a CAN source."""
    raise NotImplementedError("streaming engine not yet implemented")
