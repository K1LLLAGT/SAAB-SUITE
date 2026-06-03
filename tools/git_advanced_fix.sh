#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "        GIT ADVANCED FIXER / DOCTOR"
echo "=============================================="

# 0. Basic context
echo "[INFO] PWD: $PWD"
echo "[INFO] Repo: $(basename "$PWD")"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "[FATAL] Not inside a git repo."
    exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "[INFO] Current branch: $BRANCH"

# 1. Remote sanity
REMOTE_URL="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$REMOTE_URL" ]]; then
    echo "[WARN] No origin remote configured."
    echo "       Suggested: git remote add origin git@github.com:K1LLLAGT/SAAB_SUITE.git"
else
    echo "[INFO] origin: $REMOTE_URL"
    if [[ "$REMOTE_URL" == *SAAB-SUITE.git ]]; then
        echo "[FIX] Updating origin to SAAB_SUITE..."
        git remote set-url origin git@github.com:K1LLLAGT/SAAB_SUITE.git
        REMOTE_URL="$(git remote get-url origin)"
        echo "[INFO] origin now: $REMOTE_URL"
    fi
fi

# 2. SSH key + agent
if [[ -f ~/.ssh/id_ed25519 ]]; then
    chmod 600 ~/.ssh/id_ed25519
    chmod 644 ~/.ssh/id_ed25519.pub 2>/dev/null || true
    echo "[OK] SSH key permissions normalized"
else
    echo "[WARN] No ~/.ssh/id_ed25519 found. If pushes fail, generate one:"
    echo "       ssh-keygen -t ed25519 -C \"your_email@example.com\""
fi

if ! ssh-add -l >/dev/null 2>&1; then
    echo "[INFO] Starting ssh-agent and adding key (if present)..."
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_ed25519 2>/dev/null || echo "[WARN] Could not add id_ed25519 (may not exist)"
fi

echo "[INFO] Testing SSH to GitHub..."
SSH_OUT="$(ssh -T git@github.com 2>&1 || true)"
echo "$SSH_OUT"
if echo "$SSH_OUT" | grep -qi "successfully authenticated"; then
    echo "[OK] SSH auth to GitHub works"
else
    echo "[WARN] SSH auth not confirmed. Check https://github.com/settings/keys"
fi

# 3. Upstream tracking
UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
if [[ -z "$UPSTREAM" ]]; then
    echo "[WARN] No upstream set for $BRANCH."
    if [[ "$BRANCH" == "main" ]]; then
        echo "[FIX] Setting upstream to origin/main..."
        git branch --set-upstream-to=origin/main main 2>/dev/null || true
        UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
    fi
fi
[[ -n "$UPSTREAM" ]] && echo "[INFO] Upstream: $UPSTREAM"

# 4. Divergence status
if [[ -n "$UPSTREAM" ]]; then
    AHEAD="$(git rev-list --left-right --count "$UPSTREAM"...HEAD | awk '{print $2}')"
    BEHIND="$(git rev-list --left-right --count "$UPSTREAM"...HEAD | awk '{print $1}')"
    echo "[INFO] Ahead of $UPSTREAM by:  $AHEAD"
    echo "[INFO] Behind $UPSTREAM by:     $BEHIND"

    if (( BEHIND > 0 && AHEAD == 0 )); then
        echo "[HINT] You are behind. To update:"
        echo "       git pull --rebase"
    elif (( AHEAD > 0 && BEHIND == 0 )); then
        echo "[HINT] You are ahead. To push:"
        echo "       git push"
    elif (( AHEAD > 0 && BEHIND > 0 )); then
        echo "[HINT] History diverged. Options:"
        echo "       # Rebase:"
        echo "       git pull --rebase"
        echo "       # Or merge:"
        echo "       git pull"
        echo "       # Or force push (DANGEROUS):"
        echo "       git push --force"
    fi
fi

# 5. Working tree + index
echo "[INFO] Checking status..."
git status -sb

if ! git diff --quiet -- || ! git diff --cached --quiet --; then
    echo "[WARN] You have local changes."
    echo "       To stash: git stash push -u"
fi

# 6. Quick integrity checks
echo "[INFO] Running quick integrity checks..."
git fsck --no-dangling >/dev/null 2>&1 && echo "[OK] git fsck clean" || echo "[WARN] git fsck reported issues"

# 7. Push dry-run
echo "[INFO] Testing push (dry-run)..."
if git push --dry-run >/dev/null 2>&1; then
    echo "[OK] Dry-run push succeeded. Real push should work:"
    echo "     git push"
else
    echo "[ERROR] Dry-run push failed."
    echo "       Try:"
    echo "       git push --set-upstream origin $BRANCH"
fi

echo "=============================================="
echo "        GIT ADVANCED FIXER COMPLETE"
echo "=============================================="
