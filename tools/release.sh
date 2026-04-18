#!/usr/bin/env bash
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 <version>" >&2
    exit 1
fi

VERSION="$1"
echo "[*] Tagging v$0.1.0..."
git tag -s "v$0.1.0" -m "Release v$0.1.0"
git push origin "v$0.1.0"
echo "[*] Pushed. The release.yml workflow will take over."
