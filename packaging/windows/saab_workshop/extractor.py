"""Populate %USERPROFILE%\\SaabWorkshop\\vendor\\ from a user-chosen source.

This module is the Windows-side half of the organizer. It does NOT ship,
download, or embed any OEM binary: `source_dir` is always a path the user
supplies at runtime -- typically the vendor/ tree produced on the Termux
side by Unified_Termux_Shell_Environment_Installer.sh (synced over via a
cable/cloud folder/SD card the user already controls), or a folder on the
Windows machine where they've already installed their own licensed copies
of GDS2 / Tech2Win / GlobalTIS / etc.

If a JSONL manifest (see manifest.py) is available alongside source_dir,
each file's SHA256 is verified against it and only classification/paths
recorded in the manifest are trusted. Otherwise a local, best-effort
heuristic classifier (mirroring tools/workshop/file_organization on the
Termux side) is used.
"""

from __future__ import annotations

import re
import shutil
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .config import CATEGORY_SUBDIR, WorkshopConfig
from .logging_setup import get_logger
from .manifest import ManifestEntry, index_by_basename, load_manifest, sha256_of

_NAME_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"gds2", re.I), "gds2"),
    (re.compile(r"tech2[_ ]?win", re.I), "tech2win"),
    (re.compile(r"global[_ ]?tis", re.I), "globaltis"),
    (re.compile(r"(^|[^a-z])wis([^a-z]|$)", re.I), "wis"),
    (re.compile(r"epc[_ -]?catalog", re.I), "epc"),
    (re.compile(r"j2534", re.I), "j2534_driver"),
    (re.compile(r"mongoose", re.I), "mongoose"),
    (re.compile(r"canusb|lawicel", re.I), "canusb_driver"),
    (re.compile(r"tech2[_ -]?driver", re.I), "tech2_driver"),
]

_EXT_RULES = {
    "iso": "iso_image",
    "img": "iso_image",
    "bin": "firmware",
    "hex": "firmware",
    "s19": "firmware",
    "cal": "firmware",
    "dll": "j2534_driver",
}

_SKIP_DIR_NAMES = {".git", "__pycache__", "$RECYCLE.BIN", "System Volume Information"}


def classify(path: Path) -> str:
    name = path.name.lower()
    for pattern, category in _NAME_RULES:
        if pattern.search(name):
            return category
    ext = path.suffix.lower().lstrip(".")
    return _EXT_RULES.get(ext, "unknown")


@dataclass
class SyncResult:
    scanned: int = 0
    copied: int = 0
    skipped_unchanged: int = 0
    skipped_hash_mismatch: int = 0
    skipped_unclassified: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


def _iter_source_files(source_dir: Path) -> Iterator[Path]:
    for entry in source_dir.rglob("*"):
        if not entry.is_file():
            continue
        if any(part in _SKIP_DIR_NAMES for part in entry.parts):
            continue
        yield entry


def sync_vendor(
    config: WorkshopConfig,
    source_dir: Path,
    manifest_path: Path | None = None,
    include_unclassified: bool = False,
) -> SyncResult:
    logger = get_logger()
    result = SyncResult()

    config.ensure_directories()

    manifest_index: dict[str, ManifestEntry] = {}
    if manifest_path is not None:
        manifest_index = index_by_basename(load_manifest(manifest_path))

    if not source_dir.is_dir():
        logger.error("source directory does not exist: %s", source_dir)
        result.errors.append(f"source directory does not exist: {source_dir}")
        return result

    for src in _iter_source_files(source_dir):
        result.scanned += 1
        try:
            entry = manifest_index.get(src.name.lower())
            category = entry.category if entry else classify(src)
            src_sha256 = sha256_of(src)

            if category not in CATEGORY_SUBDIR:
                result.skipped_unclassified += 1
                if not include_unclassified:
                    continue
                subdir = "unclassified"
            else:
                subdir = CATEGORY_SUBDIR[category]

            dest_dir = config.vendor_dir / subdir
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / src.name
            if entry is not None and entry.sha256 and src_sha256 != entry.sha256:
                logger.warning(
                    "hash mismatch for %s (manifest expected %s, got %s); skipping",
                    src,
                    entry.sha256,
                    src_sha256,
                )
                result.skipped_hash_mismatch += 1
                continue

            if dest.exists() and sha256_of(dest) == src_sha256:
                result.skipped_unchanged += 1
                continue

            shutil.copy2(src, dest)

            if sha256_of(dest) != src_sha256:
                logger.error("post-copy verification failed for %s; removing partial copy", dest)
                dest.unlink(missing_ok=True)
                result.failed += 1
                result.errors.append(f"post-copy verification failed: {src}")
                continue

            result.copied += 1
            logger.info("synced [%s] %s -> %s", category, src, dest)

        except OSError as exc:
            result.failed += 1
            result.errors.append(f"{src}: {exc}")
            logger.error("failed to sync %s: %s", src, exc)

    logger.info(
        "sync complete: scanned=%d copied=%d unchanged=%d hash_mismatch=%d "
        "unclassified=%d failed=%d",
        result.scanned,
        result.copied,
        result.skipped_unchanged,
        result.skipped_hash_mismatch,
        result.skipped_unclassified,
        result.failed,
    )
    config.last_source_dir = str(source_dir)
    config.save()
    return result
