"""System-level smoke tests."""

from __future__ import annotations


def test_package_importable() -> None:
    """The top-level package imports cleanly."""
    import SAAB_SUITE
    assert SAAB_SUITE.__version__


def test_cli_module_importable() -> None:
    """The CLI module imports without instantiating Typer."""
    from SAAB_SUITE.interfaces.cli import main
    assert callable(main.main)
