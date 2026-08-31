"""Plugin contracts. Plugins implement Protocols defined in saab_suite.ports."""

from __future__ import annotations

from saab_suite.ports.can_source import ICanSource
from saab_suite.ports.flash_target import IFlashTarget

__all__ = ["ICanSource", "IFlashTarget"]
