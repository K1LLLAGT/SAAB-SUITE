#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD="$ROOT/build/appimage"
DIST="$ROOT/dist"

mkdir -p "$BUILD" "$DIST"

if ! command -v linuxdeploy >/dev/null; then
    echo "ERROR: linuxdeploy not in PATH" >&2
    exit 1
fi

# Stage Python application into AppDir
APPDIR="$BUILD/SAAB-Suite.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/lib/python3.11/site-packages"
python3 -m pip install --target "$APPDIR/usr/lib/python3.11/site-packages" "$ROOT[hardware,tui,web]"

cp "$SCRIPT_DIR/AppRun" "$APPDIR/AppRun"
cp "$SCRIPT_DIR/saab-suite.desktop" "$APPDIR/saab-suite.desktop"
chmod +x "$APPDIR/AppRun"

linuxdeploy --appdir "$APPDIR" --output appimage
mv ./SAAB-Suite-*-x86_64.AppImage "$DIST/"
echo "OK: AppImage built -> $DIST"
