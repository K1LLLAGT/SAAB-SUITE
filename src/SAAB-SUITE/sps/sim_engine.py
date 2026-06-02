from __future__ import annotations

from pathlib import Path
from saab_suite.runtime import paths


class SpsSimEngine:
    """Simulated SPS flash engine."""

    def __init__(self, vin: str, module: str, file: Path):
        self.vin = vin
        self.module = module
        self.file = file

    def run(self) -> None:
        log = paths.logs() / "sps_sim.log"
        with log.open("a", encoding="utf8") as fh:
            fh.write(f"[SPS] VIN={self.vin} MODULE={self.module} FILE={self.file}\n")
            fh.write("[SPS] Simulating flash...\n")
            fh.write("[SPS] OK\n")
