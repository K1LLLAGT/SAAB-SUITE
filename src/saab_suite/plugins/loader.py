"""Discover plugins via importlib.metadata entry points."""

from __future__ import annotations

from importlib.metadata import entry_points


def discover_can_sources() -> dict[str, type]:
    """Discover ICanSource implementations registered via entry points."""
    eps = entry_points(group="saab_suite.can_source")
    return {ep.name: ep.load() for ep in eps}


def discover_flash_targets() -> dict[str, type]:
    """Discover IFlashTarget implementations registered via entry points."""
    eps = entry_points(group="saab_suite.flash_target")
    return {ep.name: ep.load() for ep in eps}
