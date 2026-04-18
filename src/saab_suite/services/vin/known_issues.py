"""Known-issues lookup keyed by VIN-range patterns."""

from __future__ import annotations

from saab_suite.domain.vehicle.profile import KnownIssue
from saab_suite.domain.vehicle.vin import Vin


def lookup(vin: Vin) -> list[KnownIssue]:
    """Return all known issues that apply to *vin*, ordered by severity."""
    raise NotImplementedError("known issues lookup not yet implemented")
