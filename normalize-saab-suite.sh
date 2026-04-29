#!/usr/bin/env bash
set -euo pipefail

echo "[*] Normalizing SAAB-SUITE repo layout..."

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "[*] Ensuring docs/internal/ exists..."
mkdir -p docs/internal

echo "[*] Moving layout metadata into docs/internal/..."
for f in SAAB-SUITE-layout.txt SAAB-SUITE-repository-layout.txt; do
    if [ -f "$f" ]; then
        mv -v "$f" docs/internal/
    fi
done

echo "[*] Removing duplicate root README if both exist..."
if [ -f README ] && [ -f README.md ]; then
    rm -v README
fi

echo "[*] Ensuring src/tech2win is treated as generated..."
rm -rf src/tech2win

echo "[*] Normalizing packages/tech2win scripts..."
if [ -d packages/tech2win/scripts ]; then
    if [ -f packages/tech2win/scripts/extract-tech2win.sh ] && \
       [ -f packages/tech2win/scripts/extract_tech2win.sh ]; then
        rm -v packages/tech2win/scripts/extract_tech2win.sh
    fi
    chmod +x packages/tech2win/scripts/*.sh || true
fi

echo "[*] Ensuring top-level scripts are executable..."
if [ -d scripts ]; then
    find scripts -maxdepth 1 -type f -name '*.sh' -exec chmod +x {} \;
fi

echo "[*] Regenerating src/tech2win from LFS archive (if script present)..."
if [ -f packages/tech2win/scripts/extract-tech2win.sh ]; then
    mkdir -p src
    bash packages/tech2win/scripts/extract-tech2win.sh
else
    echo "[!] extract-tech2win.sh not found; skipping extraction."
fi

echo "[*] Running verify-tree.sh if present..."
if [ -f scripts/verify-tree.sh ]; then
    chmod +x scripts/verify-tree.sh
    bash scripts/verify-tree.sh || echo "[!] verify-tree.sh reported issues."
fi

echo
echo "[*] Normalization complete. Current git status:"
git status --short

echo
echo "[*] Review changes, then commit with:"
echo "    git add -A"
echo "    git commit -m \"Normalize SAAB-SUITE layout and Tech2Win workflow\""
