#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "  FIXING TEST IMPORTS (saab_suite → SAAB_SUITE)"
echo "=============================================="

# Find all files under tests/ that contain ANY reference to saab_suite
FILES=$(grep -RIl "saab_suite" tests || true)

if [ -z "$FILES" ]; then
    echo "[WARN] No test files contain 'saab_suite'"
    echo "       This means the import may be slightly different."
    echo "       Running extended search..."
    FILES=$(grep -RIl "saab" tests || true)
fi

if [ -z "$FILES" ]; then
    echo "[ERROR] No matching files found at all."
    echo "        Check if tests/ contains Python files."
    exit 1
fi

echo "[*] Patching files:"
echo "$FILES"

# Replace all variants safely
for f in $FILES; do
    sed -i \
        -e 's/from saab_suite/from SAAB_SUITE/g' \
        -e 's/import saab_suite/import SAAB_SUITE/g' \
        -e 's/saab_suite/SAAB_SUITE/g' \
        "$f"
done

echo "[OK] Test imports updated"
echo "Run: tools/bootstrap.sh"
echo "=============================================="
