"""GlobalTIS ingest -- parse procedure exports."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def parse_procedure(path: Path) -> dict[str, object]:
    """Parse a GlobalTIS procedure export."""
    raise NotImplementedError("GlobalTIS parse not yet implemented")
