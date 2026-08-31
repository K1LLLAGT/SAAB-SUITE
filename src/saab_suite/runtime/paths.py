import os
from pathlib import Path


def _default_base() -> Path:
    env = os.environ.get("SAAB_SUITE_RUNTIME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".saab" / "runtime"


BASE_DIR = _default_base()

LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
BACKUP_DIR = BASE_DIR / "backups"
LOCK_DIR = BASE_DIR / "locks"


def root() -> Path:
    """Return the runtime root directory."""
    return BASE_DIR


def logs() -> Path:
    """Return the runtime logs directory."""
    return LOG_DIR


def replay() -> Path:
    """Return the runtime replay directory."""
    return BASE_DIR / "replay"


def sps() -> Path:
    """Return the runtime SPS directory."""
    return BASE_DIR / "sps"


def vin() -> Path:
    """Return the runtime VIN directory."""
    return BASE_DIR / "vin"


def plugins() -> Path:
    """Return the runtime plugins directory."""
    return BASE_DIR / "plugins"


def cache() -> Path:
    """Return the runtime cache directory."""
    return CACHE_DIR


def ensure_dirs() -> None:
    """Create all required runtime directories if they do not exist."""
    for d in (LOG_DIR, CACHE_DIR, BACKUP_DIR, LOCK_DIR):
        d.mkdir(parents=True, exist_ok=True)
