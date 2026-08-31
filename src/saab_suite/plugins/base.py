from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Plugin(ABC):
    """Base class for SAAB Suite plugins."""

    name: str = "unnamed"

    @abstractmethod
    def activate(self) -> None:
        """Called when the plugin is loaded."""
        raise NotImplementedError

    def deactivate(self) -> None:
        """Called when the plugin is unloaded."""
        return None

    def handle_event(self, event: str, payload: Any | None = None) -> None:
        """Optional event hook."""
        return None
