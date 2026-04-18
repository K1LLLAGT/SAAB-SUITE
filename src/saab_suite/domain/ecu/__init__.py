"""ECU domain -- module identity, addressing, registry."""

from saab_suite.domain.ecu.address import CanAddressPair, KwpAddress, UdsAddress
from saab_suite.domain.ecu.module import Module, ModuleKind
from saab_suite.domain.ecu.registry import ModuleRegistry

__all__ = [
    "CanAddressPair", "KwpAddress", "Module", "ModuleKind", "ModuleRegistry", "UdsAddress",
]
