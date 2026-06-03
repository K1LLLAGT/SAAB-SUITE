from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class MockMessage:
    can_id: int
    data: bytes


class MockJ2534Adapter:
    """Simulation-only J2534 adapter for offline workflows."""

    def __init__(self) -> None:
        self._tx_log: List[MockMessage] = []

    def open(self) -> None:
        # No-op for mock
        ...

    def close(self) -> None:
        # No-op for mock
        ...

    def send(self, can_id: int, data: bytes) -> None:
        self._tx_log.append(MockMessage(can_id=can_id, data=data))

    def recv(self, timeout: float = 0.1) -> Iterable[MockMessage]:
        # For now, no incoming messages; extend as needed.
        return []

    def tx_log(self) -> List[MockMessage]:
        return list(self._tx_log)
