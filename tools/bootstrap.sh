#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo " SAAB_SUITE BOOTSTRAP: FULL SYSTEM CHECK"
echo "=============================================="

echo "[1/5] Cleanup..."
tools/cleanup.sh

echo "[2/5] Audit imports..."
tools/audit_imports.py

echo "[3/5] Verify migration..."
tools/verify_migration.py

echo "[4/5] Integrity checks..."
tools/post_migration_check.py

echo "[5/5] Running tests..."
tools/test.sh

echo "=============================================="
echo " ALL CHECKS PASSED — SAAB_SUITE IS HEALTHY"
echo "=============================================="
