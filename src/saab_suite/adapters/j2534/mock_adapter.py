from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass
class MockMessage:
    """Represent mock message."""
    can_id: int
    data: bytes


class MockJ2534Adapter:
    """Simulation-only J2534 adapter for offline workflows."""

    def __init__(self) -> None:
        self._tx_log: list[MockMessage] = []

    def open(self) -> None:
        """Open the resource."""
        # No-op for mock
        ...

    def close(self) -> None:
        """Close the resource."""
        # No-op for mock
        ...

    def send(self, can_id: int, data: bytes) -> None:
        """Send the requested payload."""
        self._tx_log.append(MockMessage(can_id=can_id, data=data))

    def recv(self, timeout: float = 0.1) -> Iterable[MockMessage]:
        # For now, no incoming messages; extend as needed.
        """Receive the next payload."""
        return []

    def tx_log(self) -> list[MockMessage]:
        """Tx Log."""
        return list(self._tx_log)
