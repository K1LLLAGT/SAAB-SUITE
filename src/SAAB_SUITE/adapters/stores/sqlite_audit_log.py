"""SQLite-backed, append-only, hash-chained audit log."""

from __future__ import annotations

from typing import TYPE_CHECKING

from SAAB_SUITE.kernel.errors import StoreError
from SAAB_SUITE.ports.audit_log import IAuditLog

if TYPE_CHECKING:
    from pathlib import Path

    from SAAB_SUITE.domain.session.audit_event import AuditEvent


class SqliteAuditLog(IAuditLog):
    """Append-only SQLite. Hash-chained. See ADR-0006."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: AuditEvent) -> AuditEvent:
        raise StoreError("audit log not yet implemented")

    def is_healthy(self) -> bool:
        raise StoreError("audit log not yet implemented")

    def verify_chain(self) -> bool:
        raise StoreError("audit log not yet implemented")
