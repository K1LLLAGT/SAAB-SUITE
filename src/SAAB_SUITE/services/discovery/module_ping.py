"""Single-module reachability check."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SAAB_SUITE.domain.ecu.module import Module
    from SAAB_SUITE.ports.uds import IUdsClient


def ping(module: Module, uds: IUdsClient, timeout_ms: int = 500) -> bool:
    """Return True if the module responds to TesterPresent."""
    raise NotImplementedError("module ping not yet implemented")
