"""DTC value object -- both ISO 15031 (5-char) and OEM raw (3-byte UDS)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DtcSystem(StrEnum):
    """First character of the 5-char DTC."""

    POWERTRAIN = "P"
    CHASSIS = "C"
    BODY = "B"
    NETWORK = "U"


class DtcKind(StrEnum):
    """Second character -- generic vs manufacturer-specific."""

    GENERIC = "0"
    MANUFACTURER = "1"
    GENERIC_2 = "2"
    MANUFACTURER_2 = "3"


@dataclass(frozen=True, slots=True)
class Dtc:
    """A diagnostic trouble code in canonical form (e.g., P0301)."""

    system: DtcSystem
    kind: DtcKind
    code: int

    def render(self) -> str:
        """Format as 5-character ISO 15031 string."""
        return f"{self.system.value}{self.kind.value}{self.code:03X}"

    @classmethod
    def from_uds_bytes(cls, raw: bytes) -> Dtc:
        """Parse a UDS 3-byte DTC (high, mid, low)."""
        if len(raw) != 3:
            msg = f"Expected 3 bytes, got {len(raw)}"
            raise ValueError(msg)
        first = (raw[0] >> 6) & 0x03
        kind_idx = (raw[0] >> 4) & 0x03
        system = [DtcSystem.POWERTRAIN, DtcSystem.CHASSIS, DtcSystem.BODY, DtcSystem.NETWORK][first]
        kind_map = {0: DtcKind.GENERIC, 1: DtcKind.MANUFACTURER, 2: DtcKind.GENERIC_2, 3: DtcKind.MANUFACTURER_2}
        code = ((raw[0] & 0x0F) << 8) | raw[1]
        return cls(system=system, kind=kind_map[kind_idx], code=code)
