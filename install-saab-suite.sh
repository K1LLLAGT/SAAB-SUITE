#!/usr/bin/env bash
set -euo pipefail

echo "[*] Installing SAAB-SUITE (Linux)..."

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "[*] Validating directory structure..."
bash scripts/verify-tree.sh

echo "[*] Extracting packages..."
bash scripts/extract-all-packages.sh

echo "[*] Creating launcher..."
cat << 'EOF' | sudo tee /usr/local/bin/saab >/dev/null
#!/usr/bin/env bash
"$ROOT/scripts/saab-suite-launcher.sh" "$@"
EOF
sudo chmod +x /usr/local/bin/saab

echo "[*] Ensuring VM directories exist..."
mkdir -p vm/WINXP-SAAB vm/Win7-SAAB

echo "[*] Installation complete."
echo "Run 'saab' to launch the suite."
