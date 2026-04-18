"""SPS session logger -- JSONL stream per flash session."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID


def open_session(session_id: UUID, log_dir: Path) -> Path:
    """Open the session log file and return its path."""
    raise NotImplementedError("SPS session logger not yet implemented")
