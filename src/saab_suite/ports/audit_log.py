"""Audit log port definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from saab_suite.domain.session.audit_event import AuditEvent


class IAuditLog(Protocol):
    """Define the append-only audit log interface."""

    def append(self, event: AuditEvent) -> AuditEvent:
        """Append an event to the audit log."""
        ...

    def is_healthy(self) -> bool:
        """Return whether the audit log backend is healthy."""
        ...

    def verify_chain(self) -> bool:
        """Verify the audit log integrity chain."""
        ...
