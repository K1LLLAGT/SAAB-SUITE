#!/usr/bin/env bash
set -euo pipefail

echo "Updating packaging metadata..."

grep -RIl "SAAB_SUITE" packaging | while read -r file; do
    sed -i 's/SAAB_SUITE/SAAB_SUITE/g' "$file"
done

grep -RIl "saab_suite" packaging | while read -r file; do
    sed -i 's/saab_suite/saab_suite/g' "$file"
done

echo "Done. Commit and push:"
echo "  git add packaging"
echo "  git commit -m \"Update packaging metadata for SAAB_SUITE\""
echo "  git push"
