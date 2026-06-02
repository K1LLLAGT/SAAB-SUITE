#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo " SAAB-SUITE BOOTSTRAP: FULL SYSTEM CHECK"
echo "=============================================="

# 1. Cleanup
echo "[1/5] Cleaning up pycache, pyc, bak..."
tools/cleanup.sh

# 2. Audit imports
echo "[2/5] Auditing for legacy imports..."
tools/audit_imports.py

# 3. Verify migration
echo "[3/5] Verifying migration..."
tools/verify_migration.py

# 4. Post-migration integrity
echo "[4/5] Running integrity checks..."
tools/post_migration_check.py

# 5. Test suite
echo "[5/5] Running test suite..."
tools/test.sh

echo "=============================================="
echo " ALL CHECKS PASSED — SAAB-SUITE IS HEALTHY"
echo "=============================================="
