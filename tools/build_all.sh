#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

echo "[*] Cleaning..."
rm -rf build/ dist/ *.egg-info src/*.egg-info

echo "[*] Building wheel + sdist..."
python -m build

echo "[*] Twine check..."
python -m twine check dist/*

if [ "${BUILD_APPIMAGE:-0}" = "1" ]; then
    echo "[*] Building AppImage..."
    bash packaging/appimage/build.sh
fi

echo "[*] Done. Artifacts in dist/"
