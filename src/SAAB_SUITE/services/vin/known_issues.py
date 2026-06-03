"""Known-issues lookup keyed by VIN-range patterns."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from SAAB_SUITE.domain.vehicle.profile import KnownIssue
    from SAAB_SUITE.domain.vehicle.vin import Vin


def lookup(vin: Vin) -> list[KnownIssue]:
    """Return all known issues that apply to *vin*, ordered by severity."""
    raise NotImplementedError("known issues lookup not yet implemented")
