"""Read and verify the JSONL manifest produced by the Termux-side organizer.

The manifest format is defined by tools/workshop/file_properties.sh
(saab_manifest_jsonl_line / saab_flush_manifest) on the Linux/Termux side.
One JSON object per line:

    {"source": "...", "category": "gds2", "label": "...",
     "destination": "vendor/isos/gds2/foo.exe", "permissions": "640",
     "required": "optional", "sha256": "<hex>", "mime": "...",
     "size_bytes": 123, "mtime_epoch": 123456789, "scanned_at": "..."}

A manifest is optional: the extractor can classify and copy files with no
manifest present (falling back to extension/name heuristics). When a
manifest *is* supplied, every copied file's SHA256 is verified against it
before the file is trusted, and a mismatch is logged and skipped rather
than raising -- a corrupt or tampered manifest must never crash the app.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .logging_setup import get_logger


@dataclass(frozen=True)
class ManifestEntry:
    source: str
    category: str
    label: str
    destination: str
    permissions: str
    required: str
    sha256: str
    mime: str
    size_bytes: int
    mtime_epoch: int
    scanned_at: str

    @property
    def basename(self) -> str:
        return Path(self.destination).name


def sha256_of(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def verify_manifest_integrity(manifest_path: Path) -> bool:
    """Checks manifest_path against its companion .sha256 side-car, if any.

    Returns True when there is no side-car to check against (nothing to
    verify) or when the side-car matches. Returns False only on a real
    mismatch -- callers should refuse to trust per-entry hashes in that case.
    """
    sidecar = manifest_path.with_name(manifest_path.name + ".sha256")
    if not sidecar.exists():
        return True
    try:
        recorded = sidecar.read_text(encoding="utf-8").split()[0]
    except (OSError, IndexError):
        return True
    actual = sha256_of(manifest_path)
    return actual is not None and actual == recorded


def load_manifest(manifest_path: Path) -> list[ManifestEntry]:
    logger = get_logger()
    entries: list[ManifestEntry] = []

    if not manifest_path.exists():
        logger.info("no manifest found at %s; proceeding without one", manifest_path)
        return entries

    if not verify_manifest_integrity(manifest_path):
        logger.error(
            "manifest checksum mismatch for %s -- ignoring its contents (extractor "
            "will fall back to heuristic classification)",
            manifest_path,
        )
        return entries

    with manifest_path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                entries.append(
                    ManifestEntry(
                        source=obj.get("source", ""),
                        category=obj.get("category", "unknown"),
                        label=obj.get("label", "Unclassified"),
                        destination=obj.get("destination", ""),
                        permissions=obj.get("permissions", "640"),
                        required=obj.get("required", "optional"),
                        sha256=obj.get("sha256", ""),
                        mime=obj.get("mime", "application/octet-stream"),
                        size_bytes=int(obj.get("size_bytes", 0)),
                        mtime_epoch=int(obj.get("mtime_epoch", 0)),
                        scanned_at=obj.get("scanned_at", ""),
                    )
                )
            except (json.JSONDecodeError, ValueError, TypeError):
                logger.warning("skipping malformed manifest line %d in %s", line_no, manifest_path)

    logger.info("loaded %d manifest entr%s from %s", len(entries), "y" if len(entries) == 1 else "ies", manifest_path)
    return entries


def index_by_basename(entries: list[ManifestEntry]) -> dict[str, ManifestEntry]:
    return {entry.basename.lower(): entry for entry in entries}


def find_latest_manifest(manifest_dir: Path) -> Path | None:
    if not manifest_dir.is_dir():
        return None
    candidates = sorted(manifest_dir.glob("manifest-*.jsonl"))
    return candidates[-1] if candidates else None
