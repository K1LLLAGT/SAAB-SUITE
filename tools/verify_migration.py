#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]

def check_git():
    out = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).decode()
    if "src/saab_suite" in out:
        print("[FAIL] src/saab_suite still present")
        sys.exit(1)
    print("[OK] No legacy package")

def check_import():
    try:
        __import__("SAAB_SUITE")
        print("[OK] Import SAAB_SUITE")
    except Exception as e:
        print("[FAIL] Import error:", e)
        sys.exit(1)

if __name__ == "__main__":
    check_git()
    check_import()
