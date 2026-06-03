"""ECU domain -- module identity, addressing, registry."""

from SAAB_SUITE.domain.ecu.address import CanAddressPair, KwpAddress, UdsAddress
from SAAB_SUITE.domain.ecu.module import Module, ModuleKind
from SAAB_SUITE.domain.ecu.registry import ModuleRegistry

__all__ = [
    "CanAddressPair", "KwpAddress", "Module", "ModuleKind", "ModuleRegistry", "UdsAddress",
]
