"""Output formatting helpers -- table / json / ndjson / yaml."""

from __future__ import annotations

import json
from typing import Any


def render(data: Any, fmt: str = "table") -> str:
    """Render *data* in the chosen format. Phase-2 will add table + yaml."""
    if fmt == "json":
        return json.dumps(data, indent=2, default=str)
    if fmt == "ndjson":
        if isinstance(data, list):
            return "\n".join(json.dumps(item, default=str) for item in data)
        return json.dumps(data, default=str)
    return str(data)
