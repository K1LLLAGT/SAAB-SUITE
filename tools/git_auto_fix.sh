#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "        GIT AUTO‑FIX FOR SAAB_SUITE"
echo "=============================================="

# 1. Detect current directory name
DIR_NAME="$(basename "$PWD")"
echo "[INFO] Current directory: $DIR_NAME"

# 2. Detect GitHub repo from remote
REMOTE_URL="$(git remote get-url origin 2>/dev/null || true)"

if [[ -z "$REMOTE_URL" ]]; then
    echo "[WARN] No origin remote found. Creating one..."
    git remote add origin git@github.com:K1LLLAGT/SAAB_SUITE.git
    REMOTE_URL="git@github.com:K1LLLAGT/SAAB_SUITE.git"
fi

echo "[INFO] Current remote: $REMOTE_URL"

# 3. Normalize remote to SSH form
if [[ "$REMOTE_URL" != git@github.com:* ]]; then
    echo "[FIX] Converting HTTPS remote → SSH remote"
    git remote set-url origin git@github.com:K1LLLAGT/SAAB_SUITE.git
fi

# 4. Ensure repo name is SAAB_SUITE
if [[ "$REMOTE_URL" == *SAAB-SUITE.git ]]; then
    echo "[FIX] Updating remote to SAAB_SUITE"
    git remote set-url origin git@github.com:K1LLLAGT/SAAB_SUITE.git
fi

# 5. Ensure SSH key permissions are correct
if [[ -f ~/.ssh/id_ed25519 ]]; then
    chmod 600 ~/.ssh/id_ed25519
    chmod 644 ~/.ssh/id_ed25519.pub
    echo "[OK] SSH key permissions fixed"
fi

# 6. Ensure SSH agent is running
if ! ssh-add -l >/dev/null 2>&1; then
    echo "[FIX] Starting ssh-agent and adding key"
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519 || true
fi

# 7. Test GitHub SSH connectivity
echo "[INFO] Testing GitHub SSH access..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "[OK] SSH authentication works"
else
    echo "[ERROR] SSH authentication failed"
    echo "Check your GitHub SSH keys: https://github.com/settings/keys"
fi

# 8. Ensure branch tracks origin/main
BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [[ "$BRANCH" != "main" ]]; then
    echo "[WARN] You are on branch $BRANCH, not main"
else
    echo "[INFO] Ensuring main tracks origin/main"
    git branch --set-upstream-to=origin/main main || true
fi

# 9. Test push
echo "[INFO] Testing git push..."
if git push --dry-run >/dev/null 2>&1; then
    echo "[OK] Push works"
else
    echo "[ERROR] Push failed — run manually:"
    echo "  git push --set-upstream origin main"
fi

echo "=============================================="
echo "        GIT AUTO‑FIX COMPLETE"
echo "=============================================="
