"""Single-module reachability check."""

from __future__ import annotations

from saab_suite.domain.ecu.module import Module
from saab_suite.ports.uds import IUdsClient


def ping(module: Module, uds: IUdsClient, timeout_ms: int = 500) -> bool:
    """Return True if the module responds to TesterPresent."""
    raise NotImplementedError("module ping not yet implemented")
