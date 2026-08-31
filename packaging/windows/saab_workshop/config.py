"""Runtime configuration for the workshop launcher.

All state lives under %USERPROFILE%\\SaabWorkshop\\ (or, off Windows,
~/SaabWorkshop, so the package can be exercised in CI/tests). Nothing here
ever points at a bundled payload -- vendor_dir is always populated by
extractor.sync_vendor() from a source the user selects at runtime.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

APP_NAME = "SaabWorkshop"

# Mirrors tools/workshop/file_organization CATEGORY_DEST in the Termux-side
# organizer, restricted to the vendor/ subtree (the only part of the repo
# layout the Windows launcher cares about).
CATEGORY_SUBDIR = {
    "gds2": "gds2",
    "tech2win": "tech2win",
    "globaltis": "globaltis",
    "wis": "wis",
    "epc": "epc",
    "j2534_driver": "j2534",
    "canusb_driver": "canusb",
    "tech2_driver": "tech2",
    "mongoose": "mongoose",
    "firmware": "firmware",
    "iso_image": "isos",
}


def default_home() -> Path:
    profile = os.environ.get("USERPROFILE") or os.environ.get("HOME") or str(Path.home())
    return Path(profile) / APP_NAME


@dataclass
class WorkshopConfig:
    home_dir: Path = field(default_factory=default_home)
    log_level: str = "INFO"
    last_source_dir: str | None = None

    @property
    def vendor_dir(self) -> Path:
        return self.home_dir / "vendor"

    @property
    def log_dir(self) -> Path:
        return self.home_dir / "logs"

    @property
    def manifest_dir(self) -> Path:
        return self.home_dir / "manifests"

    @property
    def config_path(self) -> Path:
        return self.home_dir / "config.json"

    def ensure_directories(self) -> None:
        self.home_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        for subdir in CATEGORY_SUBDIR.values():
            (self.vendor_dir / subdir).mkdir(parents=True, exist_ok=True)

    def save(self) -> None:
        self.home_dir.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["home_dir"] = str(self.home_dir)
        self.config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls) -> WorkshopConfig:
        cfg = cls()
        if cfg.config_path.exists():
            try:
                data = json.loads(cfg.config_path.read_text(encoding="utf-8"))
                if data.get("home_dir"):
                    cfg.home_dir = Path(data["home_dir"])
                cfg.log_level = data.get("log_level", cfg.log_level)
                cfg.last_source_dir = data.get("last_source_dir")
            except (OSError, json.JSONDecodeError):
                pass
        return cfg
