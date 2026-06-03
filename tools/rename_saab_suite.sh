#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "  RENAMING SAAB_SUITE → SAAB_SUITE"
echo "=============================================="

# 1. Replace all uppercase references
grep -RIl "SAAB_SUITE" . | while read -r file; do
    sed -i 's/SAAB_SUITE/SAAB_SUITE/g' "$file"
done

# 2. Replace all lowercase references
grep -RIl "saab_suite" . | while read -r file; do
    sed -i 's/saab_suite/saab_suite/g' "$file"
done

# 3. Update README clone instructions
if [ -f README.md ]; then
    sed -i 's/git clone <YOUR_REPO_URL> SAAB_SUITE/git clone <YOUR_REPO_URL> SAAB_SUITE/g' README.md
fi

# 4. Update packaging metadata
grep -RIl "SAAB_SUITE" packaging || true
grep -RIl "SAAB_SUITE" packaging | while read -r file; do
    sed -i 's/SAAB_SUITE/SAAB_SUITE/g' "$file"
done

# 5. Update docs
grep -RIl "SAAB_SUITE" docs || true
grep -RIl "SAAB_SUITE" docs | while read -r file; do
    sed -i 's/SAAB_SUITE/SAAB_SUITE/g' "$file"
done

echo "=============================================="
echo "  RENAME COMPLETE"
echo "  Next:"
echo "    git add -A"
echo "    git commit -m \"Rename SAAB_SUITE → SAAB_SUITE\""
echo "    git push --force"
echo "=============================================="
