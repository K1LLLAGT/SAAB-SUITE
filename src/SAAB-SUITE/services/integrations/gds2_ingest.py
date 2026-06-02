"""GDS2 ingest -- parse and (optionally) watch deliverable XML/zip pairs."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from saab_suite.domain.calibration.deliverable import Deliverable


def parse_deliverable(xml_path: Path) -> Deliverable:
    """Parse one GDS2 deliverable XML into a Deliverable."""
    raise NotImplementedError("GDS2 deliverable parse not yet implemented")
