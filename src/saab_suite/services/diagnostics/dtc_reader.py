"""Unified DTC reader (UDS + KWP2000)."""

from __future__ import annotations

from saab_suite.domain.dtc.code import Dtc
from saab_suite.domain.ecu.module import Module
from saab_suite.ports.kwp2000 import IKwpClient
from saab_suite.ports.uds import IUdsClient


def read_dtcs(
    module: Module,
    uds: IUdsClient | None = None,
    kwp: IKwpClient | None = None,
) -> list[Dtc]:
    """Read all stored DTCs from a module."""
    raise NotImplementedError("DTC read not yet implemented")
