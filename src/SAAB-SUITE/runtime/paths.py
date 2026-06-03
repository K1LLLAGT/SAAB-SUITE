from pathlib import Path
import os

def _default_base() -> Path:
    env = os.environ.get("SAAB_SUITE_RUNTIME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".saab-suite" / "runtime"

BASE_DIR = _default_base()

LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
BACKUP_DIR = BASE_DIR / "backups"
LOCK_DIR = BASE_DIR / "locks"

def ensure_dirs():
    for d in (LOG_DIR, CACHE_DIR, BACKUP_DIR, LOCK_DIR):
        d.mkdir(parents=True, exist_ok=True)
