"""VIN value object. 17-character ISO 3779 vehicle identification number."""

from __future__ import annotations

import re

from saab_suite.kernel.errors import InvalidVinError

_VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")
_TRANSLITERATION = {
    **dict.fromkeys("AJ", 1),
    **dict.fromkeys("BKS", 2),
    **dict.fromkeys("CLT", 3),
    **dict.fromkeys("DMU", 4),
    **dict.fromkeys("ENV", 5),
    **dict.fromkeys("FW", 6),
    **dict.fromkeys("GPX", 7),
    **dict.fromkeys("HY", 8),
    **dict.fromkeys("RZ", 9),
}
_WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2)


class Vin(str):
    """17-character VIN. Validated at construction; immutable.

    Validation:
        - length 17
        - charset [A-HJ-NPR-Z0-9] (no I, O, Q)

    Check-digit verification is exposed via :meth:`is_north_american_check_valid`
    rather than enforced at construction, because ROW VINs may not satisfy the
    NA check digit rule.
    """

    __slots__ = ()

    def __new__(cls, value: str) -> "Vin":
        upper = value.upper()
        if not _VIN_PATTERN.match(upper):
            msg = f"Invalid VIN: {value!r} (must be 17 chars, no I/O/Q)"
            raise InvalidVinError(msg)
        return super().__new__(cls, upper)

    @property
    def wmi(self) -> str:
        """World Manufacturer Identifier (positions 1-3)."""
        return self[0:3]

    @property
    def vds(self) -> str:
        """Vehicle Descriptor Section (positions 4-9)."""
        return self[3:9]

    @property
    def vis(self) -> str:
        """Vehicle Identifier Section (positions 10-17)."""
        return self[9:17]

    @property
    def model_year_char(self) -> str:
        """Position 10 -- encodes model year per ISO standard."""
        return self[9]

    @property
    def check_digit(self) -> str:
        """Position 9 -- North American check digit (or 0 for ROW)."""
        return self[8]

    def is_north_american_check_valid(self) -> bool:
        """Verify North American VIN check digit (position 9)."""
        total = 0
        for ch, weight in zip(self, _WEIGHTS, strict=True):
            value = _TRANSLITERATION.get(ch, int(ch) if ch.isdigit() else None)
            if value is None:
                return False
            total += value * weight
        remainder = total % 11
        expected = "X" if remainder == 10 else str(remainder)
        return self.check_digit == expected
