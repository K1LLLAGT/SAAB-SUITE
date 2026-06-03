"""Unified DTC reader (UDS + KWP2000)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SAAB_SUITE.domain.dtc.code import Dtc
    from SAAB_SUITE.domain.ecu.module import Module
    from SAAB_SUITE.ports.kwp2000 import IKwpClient
    from SAAB_SUITE.ports.uds import IUdsClient


def read_dtcs(
    module: Module,
    uds: IUdsClient | None = None,
    kwp: IKwpClient | None = None,
) -> list[Dtc]:
    """Read all stored DTCs from a module."""
    raise NotImplementedError("DTC read not yet implemented")
