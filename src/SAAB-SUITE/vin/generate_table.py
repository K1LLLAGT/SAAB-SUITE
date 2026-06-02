from __future__ import annotations

import json
from pathlib import Path


def generate_from_csv(csv_file: Path, out_file: Path) -> None:
    """Generate VIN prefix table from EPC/WIS CSV export.

    Expected CSV columns:
        prefix,model,year,engine
    """
    table = {}
    with csv_file.open("r", encoding="utf8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            prefix, model, year, engine = line.split(",")
            table[prefix] = {
                "model": model,
                "year": year,
                "engine": engine,
            }

    with out_file.open("w", encoding="utf8") as fh:
        json.dump(table, fh, indent=2)
