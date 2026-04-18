"""Verifies the import-linter contracts run cleanly.

This is the architecture's safety net. If a future change violates the
hexagonal layering, this test fails before any merge.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

import pytest


@pytest.mark.integration
def test_import_linter_contracts_pass() -> None:
    if shutil.which("lint-imports") is None:
        pytest.skip("lint-imports not installed (pip install -e \".[dev]\")")
    result = subprocess.run(
        ["lint-imports"],
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    assert result.returncode == 0, "import-linter contracts failed"
