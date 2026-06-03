#!/usr/bin/env bash
set -euo pipefail

mkdir -p tools

cat > tools/update_badges.sh << 'INNER'
#!/usr/bin/env bash
set -euo pipefail

echo "Updating badges in README.md..."

sed -i 's/SAAB_SUITE/SAAB_SUITE/g' README.md
sed -i 's/saab_suite/saab_suite/g' README.md

echo "Done. Commit and push:"
echo "  git add README.md"
echo "  git commit -m \"Update badges for SAAB_SUITE\""
echo "  git push"
INNER

chmod +x tools/update_badges.sh
echo "[OK] Created tools/update_badges.sh"
