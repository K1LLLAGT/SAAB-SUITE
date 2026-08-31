"""Logging configuration shared by the CLI, GUI, extractor, and launcher.

Every entrypoint in this package calls configure_logging() exactly once.
Handlers are best-effort: if the log directory cannot be created (locked
down profile, read-only mount), logging silently falls back to console
only rather than crashing the application.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

_LOGGER_NAME = "saab_workshop"


def configure_logging(log_dir: Path | None, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    if log_dir is not None:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            file_handler = logging.FileHandler(
                log_dir / f"saab-workshop-{stamp}.log", encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError:
            logger.warning("could not open log directory %s; console logging only", log_dir)

    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)
