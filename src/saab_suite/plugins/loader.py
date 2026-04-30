from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import List

from saab_suite.plugins.base import Plugin
from saab_suite.runtime import paths


def load_plugins() -> List[Plugin]:
    plugins: List[Plugin] = []

    # 1. Load entry point plugins
    try:
        import pkg_resources
        for ep in pkg_resources.iter_entry_points("saab_suite.plugins"):
            plugin_cls = ep.load()
            plugins.append(plugin_cls())
    except Exception:
        pass

    # 2. Load runtime plugins
    runtime_dir = paths.plugins()
    sys.path.insert(0, str(runtime_dir))

    for file in runtime_dir.glob("*.py"):
        mod_name = file.stem
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "PluginImpl"):
            plugins.append(mod.PluginImpl())

    return plugins
