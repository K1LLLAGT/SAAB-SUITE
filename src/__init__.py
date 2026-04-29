"""
SAAB-SUITE: Full SAAB/GM diagnostic suite.
"""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("saab-suite")
except PackageNotFoundError:
    __version__ = "1.0.0"

__all__ = [
    "engine",
    "can",
    "j2534",
    "gds2",
    "sps",
    "ui",
    "tui",
    "analysis",
]
