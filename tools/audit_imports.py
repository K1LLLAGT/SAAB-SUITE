#!/usr/bin/env python3
from pathlib import Path
import ast

ROOT = Path("src/SAAB-SUITE")

missing = []

for py in ROOT.rglob("*.py"):
    tree = ast.parse(py.read_text(), filename=str(py))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("saab_suite"):
                missing.append((py, node.module))

if missing:
    print("Legacy imports found:")
    for path, mod in missing:
        print(f"{path}: from {mod}")
else:
    print("No legacy imports.")
