"""UDS DTC status byte semantics (ISO 14229-1 Annex D)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DtcStatus:
    """Decoded UDS DTC status byte."""

    raw: int

    @property
    def test_failed(self) -> bool:
        return bool(self.raw & 0x01)

    @property
    def test_failed_this_op_cycle(self) -> bool:
        return bool(self.raw & 0x02)

    @property
    def pending(self) -> bool:
        return bool(self.raw & 0x04)

    @property
    def confirmed(self) -> bool:
        return bool(self.raw & 0x08)

    @property
    def test_not_completed_since_clear(self) -> bool:
        return bool(self.raw & 0x10)

    @property
    def test_failed_since_clear(self) -> bool:
        return bool(self.raw & 0x20)

    @property
    def test_not_completed_this_op_cycle(self) -> bool:
        return bool(self.raw & 0x40)

    @property
    def warning_indicator_requested(self) -> bool:
        return bool(self.raw & 0x80)
