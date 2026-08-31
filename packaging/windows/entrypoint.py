"""PyInstaller entry point.

PyInstaller executes its target script as a top-level module with no
package context, so `saab_workshop/__main__.py` (which uses a relative
import for `python -m saab_workshop` support) cannot be used directly as
the Analysis script. This wrapper imports the package absolutely instead
and is what saab_workshop.spec points at.
"""

from saab_workshop.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
