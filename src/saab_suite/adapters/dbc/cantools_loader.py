"""DBC loader wrapping the ``cantools`` library behind a domain facade.

The kernel never sees a ``cantools.Message``. This module is the only place
that imports cantools.
"""

from __future__ import annotations

from pathlib import Path

from saab_suite.domain.can.frame import CanId
from saab_suite.domain.can.signal import SignalDescriptor


class DbcIndex:
    """Indexed view of a DBC file. Phase-2."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def lookup(self, can_id: CanId) -> list[SignalDescriptor]:
        """Return the signal descriptors carried by *can_id*."""
        raise NotImplementedError("DBC loader not yet implemented")
