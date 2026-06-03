#!/usr/bin/env bash
set -euo pipefail

PREFIX_DIR="${PREFIX:-/data/data/com.termux/files/usr}"
APP_DIR="$PREFIX_DIR/share/saab-suite"

mkdir -p "$APP_DIR"
cp -r . "$APP_DIR"

if ! grep -q "SAAB_SUITE_RUNTIME" "$HOME/.bashrc"; then
  echo 'export SAAB_SUITE_RUNTIME="$HOME/.saab-suite/runtime"' >> "$HOME/.bashrc"
fi

echo "Installed SAAB-SUITE to $APP_DIR"
