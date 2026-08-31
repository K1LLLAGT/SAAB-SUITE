from __future__ import annotations

import importlib
import logging
import sys
from typing import TYPE_CHECKING

from saab_suite.runtime import paths

if TYPE_CHECKING:
    from saab_suite.plugins.base import Plugin

logger = logging.getLogger(__name__)


def load_plugins() -> list[Plugin]:
    """Load plugins."""
    plugins: list[Plugin] = []

    # 1. Load entry point plugins
    try:
        import pkg_resources
        for ep in pkg_resources.iter_entry_points("saab_suite.plugins"):
            try:
                plugin_cls = ep.load()
                plugins.append(plugin_cls())
            except Exception:
                logger.exception("Failed to load plugin %s", ep.name)
    except Exception:
        logger.exception("Failed to enumerate plugin entry points")

    # 2. Load runtime plugins
    runtime_dir = paths.plugins()
    sys.path.insert(0, str(runtime_dir))

    for file in runtime_dir.glob("*.py"):
        mod_name = file.stem
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "PluginImpl"):
            plugins.append(mod.PluginImpl())

    return plugins
