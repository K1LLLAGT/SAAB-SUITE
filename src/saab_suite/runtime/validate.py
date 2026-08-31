from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from saab_suite.runtime import paths


@dataclass
class PathStatus:
    """Status of a single runtime directory path."""

    name: str
    path: Path
    exists: bool
    is_dir: bool


def validate_tree() -> list[PathStatus]:
    """Return validation status for all expected runtime directories."""
    checks = [
        ("root", paths.root()),
        ("logs", paths.logs()),
        ("replay", paths.replay()),
        ("sps", paths.sps()),
        ("vin", paths.vin()),
        ("plugins", paths.plugins()),
        ("cache", paths.cache()),
    ]
    result: list[PathStatus] = []
    for name, p in checks:
        result.append(PathStatus(name=name, path=p, exists=p.exists(), is_dir=p.is_dir()))
    return result
