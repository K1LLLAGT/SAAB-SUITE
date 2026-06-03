"""Plugin contracts. Plugins implement Protocols defined in SAAB_SUITE.ports."""

from __future__ import annotations

from SAAB_SUITE.ports.can_source import ICanSource
from SAAB_SUITE.ports.flash_target import IFlashTarget

__all__ = ["ICanSource", "IFlashTarget"]
