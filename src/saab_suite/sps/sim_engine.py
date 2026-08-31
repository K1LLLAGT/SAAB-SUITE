from __future__ import annotations

from typing import TYPE_CHECKING

from saab_suite.runtime import paths

if TYPE_CHECKING:
    from pathlib import Path


class SpsSimEngine:
    """Simulated SPS flash engine."""

    def __init__(self, vin: str, module: str, file: Path):
        self.vin = vin
        self.module = module
        self.file = file

    def run(self) -> None:
        """Run the operation."""
        log = paths.logs() / "sps_sim.log"
        with log.open("a", encoding="utf8") as fh:
            fh.write(f"[SPS] VIN={self.vin} MODULE={self.module} FILE={self.file}\n")
            fh.write("[SPS] Simulating flash...\n")
            fh.write("[SPS] OK\n")
