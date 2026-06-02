#!/usr/bin/env bash
# Remove tracked cruft from adapters/can/ and stop it coming back.
# Run from anywhere inside the repo.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

CAN="src/saab_suite/adapters/can"

echo "Removing stale backup files..."
git rm -f "$CAN/remote_interface.py.bak" "$CAN/remote_interface.py.bak.bak" 2>/dev/null || true

echo "Untracking committed bytecode..."
git rm -r --cached "$CAN/__pycache__" 2>/dev/null || true
find . -name '__pycache__' -type d -prune -exec git rm -r --cached {} + 2>/dev/null || true

echo "Updating .gitignore..."
for pat in '__pycache__/' '*.py[cod]' '*.bak' '*.bak.*'; do
    grep -qxF "$pat" .gitignore 2>/dev/null || echo "$pat" >> .gitignore
done

echo
echo "Done. Review with:  git status"
echo "Then commit:        git commit -m 'Clean up adapters/can: drop backups and tracked bytecode'"
