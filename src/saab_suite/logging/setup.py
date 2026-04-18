"""structlog configuration."""

from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure stdlib + structlog. Phase-2 wires the full pipeline."""
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))
