#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dist"
VERSION="$(git describe --tags --always --dirty)"

echo "[*] Building SAAB-SUITE release: $VERSION"

rm -rf "$OUT"
mkdir -p "$OUT"

TMP="$(mktemp -d)"
cp -r "$ROOT" "$TMP/SAAB-SUITE"

cd "$TMP/SAAB-SUITE"

echo "[*] Running normalization..."
chmod +x normalize-saab-suite.sh
./normalize-saab-suite.sh

echo "[*] Removing generated artifacts..."
rm -rf src/tech2win
rm -rf packages/tech2win/Tech2Win_extracted

echo "[*] Stamping version..."
echo "$VERSION" > VERSION.txt

echo "[*] Creating ZIP..."
cd "$TMP"
zip -r "$OUT/SAAB-SUITE-$VERSION.zip" SAAB-SUITE >/dev/null

echo "[*] Release built:"
echo "    $OUT/SAAB-SUITE-$VERSION.zip"
