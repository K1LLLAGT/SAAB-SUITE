"""Checksum expectations for a firmware image."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChecksumExpectation:
    """Expected checksums for a firmware image."""

    sha256: str
    crc32: int
    region_start: int = 0
    region_end: int | None = None
