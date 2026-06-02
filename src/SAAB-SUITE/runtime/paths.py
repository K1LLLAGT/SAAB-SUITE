from __future__ import annotations

import os
from pathlib import Path

_TERMUX_DEFAULT_ROOT = Path.home() / "saab-runtime"


def root() -> Path:
    """Return the runtime root directory.

    Overridable via SAAB_RUNTIME_ROOT.
    """
    override = os.getenv("SAAB_RUNTIME_ROOT")
    base = Path(override).expanduser() if override else _TERMUX_DEFAULT_ROOT
    base.mkdir(parents=True, exist_ok=True)
    return base


def logs() -> Path:
    path = root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def replay() -> Path:
    path = root() / "replay"
    path.mkdir(parents=True, exist_ok=True)
    return path


def sps() -> Path:
    path = root() / "sps"
    path.mkdir(parents=True, exist_ok=True)
    return path


def vin() -> Path:
    path = root() / "vin"
    path.mkdir(parents=True, exist_ok=True)
    return path


def plugins() -> Path:
    path = root() / "plugins"
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache() -> Path:
    path = root() / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path
