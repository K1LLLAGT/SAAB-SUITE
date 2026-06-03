"""``saab-tui`` entry point."""

from __future__ import annotations


def main() -> None:
    """Launch the TUI."""
    raise NotImplementedError("TUI not yet implemented")


if __name__ == "__main__":
    main()

from SAAB_SUITE.interfaces.tui.screens.workflow import WorkflowScreen

# Example: add to your screen routing / menu
# self.push_screen("workflow", WorkflowScreen())
