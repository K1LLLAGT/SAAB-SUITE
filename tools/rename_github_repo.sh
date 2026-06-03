#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: $0 <old_name> <new_name>"
    exit 1
fi

OLD="$1"
NEW="$2"

echo "Renaming GitHub repo: \$OLD → \$NEW"

curl -X PATCH \
  -H "Authorization: token \$GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/\$GITHUB_USER/\$OLD \
  -d "{\"name\": \"\$NEW\"}"

echo "Done. Update remotes:"
echo "  git remote set-url origin git@github.com:\$GITHUB_USER/\$NEW.git"
