"""IAuditLog -- append-only, hash-chained audit log."""

from __future__ import annotations

from typing import Protocol

from saab_suite.domain.session.audit_event import AuditEvent


class IAuditLog(Protocol):
    """Append-only audit log with hash chaining."""

    def append(self, event: AuditEvent) -> AuditEvent: ...
    def is_healthy(self) -> bool: ...
    def verify_chain(self) -> bool: ...
