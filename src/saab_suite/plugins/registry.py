"""In-memory plugin registry built from discovered entry points."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PluginRegistry:
    """Registered plugin classes by group."""

    can_sources: dict[str, type] = field(default_factory=dict)
    flash_targets: dict[str, type] = field(default_factory=dict)
    tui_screens: dict[str, type] = field(default_factory=dict)
    fault_patterns: dict[str, type] = field(default_factory=dict)
