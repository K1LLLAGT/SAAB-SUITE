"""System-level smoke tests."""

from __future__ import annotations


def test_package_importable() -> None:
    """The top-level package imports cleanly."""
    import saab_suite
    assert saab_suite.__version__


def test_cli_module_importable() -> None:
    """The CLI module imports without instantiating Typer."""
    from saab_suite.interfaces.cli import main
    assert callable(main.main)
