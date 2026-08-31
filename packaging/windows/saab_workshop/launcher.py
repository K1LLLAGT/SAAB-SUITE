"""Unified launcher for OEM tools found under vendor/.

Never raises out to the caller: every public function returns a
LaunchResult / list, and every failure mode (missing vendor/ subdir, no
matching executable, launch failure, unreadable file) is logged and
reported back as data, not an exception. This is a deliberate design
requirement -- a diagnostics workstation launcher must not crash a working
session over one missing or renamed tool.
"""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import WorkshopConfig
from .logging_setup import get_logger
from .manifest import find_latest_manifest, index_by_basename, load_manifest, sha256_of

# category -> (display name, subdir under vendor/, executable name globs)
TOOL_REGISTRY: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "gds2": ("GDS2", "gds2", ("GDS2.exe", "Gds2.exe", "*GDS2*.exe")),
    "tech2win": ("Tech2Win", "tech2win", ("Tech2Win.exe", "*Tech2Win*.exe")),
    "globaltis": ("GlobalTIS", "globaltis", ("GlobalTIS.exe", "*GlobalTIS*.exe", "*TIS*.exe")),
    "wis": ("WIS", "wis", ("*WIS*.exe",)),
    "epc": ("EPC", "epc", ("*EPC*.exe",)),
    "j2534_driver": ("J2534 Toolbox", "j2534", ("*J2534*.exe", "*Toolbox*.exe")),
    "mongoose": ("Mongoose Configurator", "mongoose", ("*Mongoose*.exe",)),
    "canusb_driver": ("CANUSB Utility", "canusb", ("*CANUSB*.exe", "*Lawicel*.exe")),
    "tech2_driver": ("Tech2 Driver Utility", "tech2", ("*Tech2*.exe",)),
}


@dataclass
class LaunchResult:
    ok: bool
    message: str
    category: str | None = None
    path: Path | None = None


def find_tools(config: WorkshopConfig, category: str) -> list[Path]:
    logger = get_logger()
    entry = TOOL_REGISTRY.get(category)
    if entry is None:
        logger.warning("unknown tool category requested: %s", category)
        return []

    _, subdir, patterns = entry
    search_dir = config.vendor_dir / subdir
    if not search_dir.is_dir():
        logger.info("vendor subdirectory not present (nothing installed yet): %s", search_dir)
        return []

    found: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for candidate in search_dir.rglob(pattern):
            if candidate.is_file() and candidate not in seen:
                seen.add(candidate)
                found.append(candidate)
    return sorted(found)


def list_available_tools(config: WorkshopConfig) -> dict[str, list[Path]]:
    return {category: find_tools(config, category) for category in TOOL_REGISTRY}


def _verify_against_manifest(config: WorkshopConfig, path: Path) -> tuple[bool, str]:
    manifest_path = find_latest_manifest(config.manifest_dir)
    if manifest_path is None:
        return True, "no manifest available; launching without integrity check"

    index = index_by_basename(load_manifest(manifest_path))
    entry = index.get(path.name.lower())
    if entry is None or not entry.sha256:
        return True, "file not present in manifest; launching without integrity check"

    actual = sha256_of(path)
    if actual is None:
        return False, f"could not read {path} for integrity check"
    if actual != entry.sha256:
        return False, f"SHA256 mismatch (manifest={entry.sha256}, actual={actual})"
    return True, "SHA256 verified against manifest"


def launch_tool(
    config: WorkshopConfig,
    category: str,
    index: int = 0,
    verify: bool = True,
) -> LaunchResult:
    logger = get_logger()
    try:
        candidates = find_tools(config, category)
        if not candidates:
            display = TOOL_REGISTRY.get(category, (category,))[0]
            msg = (
                f"{display} not found under {config.vendor_dir}. "
                "Run 'extract' first, or install it there manually."
            )
            logger.warning(msg)
            return LaunchResult(ok=False, message=msg, category=category)

        if index < 0 or index >= len(candidates):
            msg = (
                f"tool index {index} out of range for category {category} ({len(candidates)} found)"
            )
            logger.warning(msg)
            return LaunchResult(ok=False, message=msg, category=category)

        target = candidates[index]

        if verify:
            ok, detail = _verify_against_manifest(config, target)
            logger.info("integrity check for %s: %s", target, detail)
            if not ok:
                msg = f"refusing to launch {target}: {detail}"
                logger.error(msg)
                return LaunchResult(ok=False, message=msg, category=category, path=target)

        if platform.system() != "Windows":
            msg = f"not launching {target}: not running on Windows (platform={platform.system()})"
            logger.info(msg)
            return LaunchResult(ok=False, message=msg, category=category, path=target)

        subprocess.Popen([str(target)], cwd=str(target.parent))  # noqa: S603
        msg = f"launched {target}"
        logger.info(msg)
        return LaunchResult(ok=True, message=msg, category=category, path=target)

    except OSError as exc:
        msg = f"failed to launch tool for category {category}: {exc}"
        logger.error(msg)
        return LaunchResult(ok=False, message=msg, category=category)
    except Exception as exc:
        msg = f"unexpected error launching tool for category {category}: {exc}"
        logger.error(msg)
        return LaunchResult(ok=False, message=msg, category=category)
