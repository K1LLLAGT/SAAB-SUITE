"""Canonical module catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saab_suite.domain.ecu.module import Module, ModuleKind


@dataclass(frozen=True, slots=True)
class ModuleRegistry:
    """Lookup table for canonical modules."""

    by_kind: dict[ModuleKind, Module]

    def get(self, kind: ModuleKind) -> Module | None:
        """Return the canonical module for *kind*, or None."""
        return self.by_kind.get(kind)

    def all(self) -> tuple[Module, ...]:
        """Return all registered modules in registration order."""
        return tuple(self.by_kind.values())
