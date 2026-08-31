#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def check_git():
    """Check Git."""
    git = shutil.which("git")
    if git is None:
        msg = "git executable not found"
        raise RuntimeError(msg)
    out = subprocess.check_output([git, "status", "--porcelain"], cwd=ROOT).decode()  # noqa: S603
    if "src/saab_suite" in out:
        print("[FAIL] src/saab_suite still present")
        sys.exit(1)
    print("[OK] No legacy package")

def check_import():
    """Check Import."""
    try:
        __import__("saab_suite")
        print("[OK] Import saab_suite")
    except Exception as e:
        print("[FAIL] Import error:", e)
        sys.exit(1)

if __name__ == "__main__":
    check_git()
    check_import()
