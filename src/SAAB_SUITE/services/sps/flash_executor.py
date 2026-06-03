"""SPS flash executor.

Accepts ONLY :class:`ValidatedFlashPlan`. There is no path here that bypasses
validation -- that is the central safety property. See ADR-0003 and
``SECURITY.md``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from SAAB_SUITE.kernel.errors import FlashAborted

if TYPE_CHECKING:
    from SAAB_SUITE.ports.audit_log import IAuditLog
    from SAAB_SUITE.ports.flash_target import IFlashTarget
    from SAAB_SUITE.services.sps.plan_validator import ValidatedFlashPlan


def execute(
    validated: ValidatedFlashPlan,
    target: IFlashTarget,
    audit: IAuditLog,
    confirm_token: str,
) -> None:
    """Execute a validated flash plan.

    The provided ``confirm_token`` must equal ``validated.confirm_token``;
    mismatch raises FlashAborted before any I/O is performed.

    Raises:
        FlashAborted: token mismatch, kill switch unset, lock contention.
    """
    if confirm_token != validated.confirm_token:
        msg = "confirm token does not match validated plan"
        raise FlashAborted(msg)
    raise NotImplementedError("SPS flash execution not yet implemented")
