#!/usr/bin/env bash
set -euo pipefail

mkdir -p tools

cat > tools/master_repo_update.sh << 'INNER'
#!/usr/bin/env bash
set -euo pipefail

OLD="SAAB_SUITE"
NEW="SAAB_SUITE"

echo "=============================================="
echo "  MASTER REPO UPDATE: \$OLD → \$NEW"
echo "=============================================="

echo "[1/7] Renaming GitHub repository..."
tools/rename_github_repo.sh "\$OLD" "\$NEW"

echo "[2/7] Updating local repo references..."
tools/rename_saab_suite.sh

echo "[3/7] Updating badges..."
tools/update_badges.sh

echo "[4/7] Updating packaging metadata..."
tools/update_packaging_metadata.sh

echo "[5/7] Regenerating README..."
tools/regenerate_readme.sh

echo "[6/7] Committing changes..."
git add -A
git commit -m "Master update: rename repo, update badges, packaging, README" || true

echo "[7/7] Force pushing to new remote..."
git remote set-url origin "git@github.com:\$GITHUB_USER/\$NEW.git"
git push --force

echo "=============================================="
echo "  MASTER UPDATE COMPLETE"
echo "  Repo is now: https://github.com/\$GITHUB_USER/\$NEW"
echo "=============================================="
INNER

chmod +x tools/master_repo_update.sh
echo "[OK] Created tools/master_repo_update.sh"
