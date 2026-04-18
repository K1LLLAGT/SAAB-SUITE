"""Calibration comparator -- diff two calibration images."""

from __future__ import annotations

from dataclasses import dataclass

from saab_suite.domain.firmware.image import FirmwareImage


@dataclass(frozen=True, slots=True)
class CalibrationDiff:
    """Structured diff between two calibrations."""

    added_maps: tuple[str, ...]
    removed_maps: tuple[str, ...]
    changed_bytes: int


def compare(a: FirmwareImage, b: FirmwareImage) -> CalibrationDiff:
    """Diff two calibration images."""
    raise NotImplementedError("cal compare not yet implemented")
