#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "  FIXING CLI ENTRYPOINTS (saab → saab)"
echo "=============================================="

# 1. Fix post_migration_check.py
echo "[*] Patching tools/post_migration_check.py..."
sed -i 's/saab/saab/g' tools/post_migration_check.py

# 2. Fix bootstrap scripts (if any reference old name)
echo "[*] Scanning tools/ for old CLI references..."
grep -rl "saab" tools || true
grep -rl "saab" tools | xargs sed -i 's/saab/saab/g' || true

# 3. Fix merge scripts
echo "[*] Scanning merge scripts..."
grep -rl "saab" tools/merge* || true
grep -rl "saab" tools/merge* | xargs sed -i 's/saab/saab/g' || true

# 4. Fix super-bootstrap generator
echo "[*] Scanning super bootstrap generator..."
grep -rl "saab" tools/super_bootstrap_generator.sh || true
sed -i 's/saab/saab/g' tools/super_bootstrap_generator.sh || true

# 5. Fix any CLI references in docs
echo "[*] Updating docs..."
grep -rl "saab" docs || true
grep -rl "saab" docs | xargs sed -i 's/saab/saab/g' || true

# 6. Fix any CLI references in source tree
echo "[*] Updating source tree..."
grep -rl "saab" src || true
grep -rl "saab" src | xargs sed -i 's/saab/saab/g' || true

echo "=============================================="
echo "  CLI ENTRYPOINT PATCH COMPLETE"
echo "  Run: tools/bootstrap.sh"
echo "=============================================="
