from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Optional


@dataclass
class VinInfo:
    vin: str
    model: str
    year: str
    engine: str


def _load_table() -> dict:
    data_path = files("saab_suite.data.vin") / "saab_vin_table.json"
    with data_path.open("r", encoding="utf8") as fh:
        return json.load(fh)


_TABLE = _load_table()


def decode_vin(vin: str) -> Optional[VinInfo]:
    vin = vin.strip().upper()
    if len(vin) != 17:
        return None

    prefix = vin[:8]
    entry = _TABLE.get(prefix)
    if not entry:
        return None

    return VinInfo(
        vin=vin,
        model=entry.get("model", "unknown"),
        year=entry.get("year", "unknown"),
        engine=entry.get("engine", "unknown"),
    )
