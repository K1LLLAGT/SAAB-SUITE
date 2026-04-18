"""Protocol detection -- UDS / KWP2000 / GMLAN."""

from __future__ import annotations

from enum import Enum

from saab_suite.domain.ecu.module import Module
from saab_suite.ports.kwp2000 import IKwpClient
from saab_suite.ports.uds import IUdsClient


class DetectedProtocol(str, Enum):
    """Diagnostic protocol detected for a module."""

    UDS = "UDS"
    KWP2000 = "KWP2000"
    GMLAN = "GMLAN"
    UNKNOWN = "UNKNOWN"


def detect(
    module: Module,
    uds: IUdsClient | None,
    kwp: IKwpClient | None,
) -> DetectedProtocol:
    """Detect which diagnostic protocol the module speaks."""
    raise NotImplementedError("protocol detection not yet implemented")
