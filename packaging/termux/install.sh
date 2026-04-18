#!/data/data/com.termux/files/usr/bin/env bash
set -euo pipefail

echo "[*] Updating packages..."
pkg update -y && pkg upgrade -y

echo "[*] Installing system deps..."
pkg install -y python git rust libffi openssl clang

echo "[*] Installing saab-suite (no hardware extras under Termux)..."
pip install --upgrade pip
pip install -e "$(dirname "$0")/../.."[tui,web,dev]

echo "[*] Done. Try: saab version"
