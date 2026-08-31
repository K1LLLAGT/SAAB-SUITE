"""SPS recovery -- resume aborted flash sessions from session log."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


def resume(session_id: UUID) -> None:
    """Resume an aborted flash session from the last acknowledged block."""
    raise NotImplementedError("SPS recovery not yet implemented")
