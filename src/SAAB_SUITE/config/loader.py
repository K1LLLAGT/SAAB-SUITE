"""Layered config loader: defaults / system / user / project / env / CLI."""

from __future__ import annotations

from SAAB_SUITE.config.schema import SaabSuiteConfig


def load_config() -> SaabSuiteConfig:
    """Load configuration. Phase-2 implements the full layering."""
    return SaabSuiteConfig()
