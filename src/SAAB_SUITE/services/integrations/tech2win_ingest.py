"""Tech2Win ingest -- parse session log exports."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def parse_session(path: Path) -> dict[str, object]:
    """Parse a Tech2Win session export."""
    raise NotImplementedError("Tech2Win parse not yet implemented")
