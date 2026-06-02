"""Layered config loader: defaults / system / user / project / env / CLI."""

from __future__ import annotations

from saab_suite.config.schema import SaabSuiteConfig


def load_config() -> SaabSuiteConfig:
    """Load configuration. Phase-2 implements the full layering."""
    return SaabSuiteConfig()
