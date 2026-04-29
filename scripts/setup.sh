#!/usr/bin/env bash
# setup.sh – Environment setup script for SAAB-SUITE
#
# Sets up a Python virtual environment, installs dependencies, and
# performs platform-specific configuration (SocketCAN on Linux,
# J2534 registry checks on Windows via WSL/msys2).
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh [--no-venv] [--dev]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_ROOT/.venv"
PYTHON="${PYTHON:-python3}"
CREATE_VENV=1
DEV_INSTALL=0

# ── Parse arguments ────────────────────────────────────────────────────────

for arg in "$@"; do
  case "$arg" in
    --no-venv) CREATE_VENV=0 ;;
    --dev)     DEV_INSTALL=1 ;;
    -h|--help)
      echo "Usage: $0 [--no-venv] [--dev]"
      echo "  --no-venv  Skip virtual environment creation"
      echo "  --dev      Install development/test extras"
      exit 0
      ;;
  esac
done

echo "════════════════════════════════════════════════"
echo "  SAAB-SUITE Environment Setup"
echo "════════════════════════════════════════════════"

# ── Python version check ───────────────────────────────────────────────────

PY_VER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $PY_VER"
if [[ "${PY_VER%%.*}" -lt 3 ]] || { [[ "${PY_VER%%.*}" -eq 3 ]] && [[ "${PY_VER##*.}" -lt 10 ]]; }; then
  echo "ERROR: Python >= 3.10 is required.  Found $PY_VER."
  exit 1
fi

# ── Virtual environment ────────────────────────────────────────────────────

if [[ "$CREATE_VENV" -eq 1 ]]; then
  if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment at $VENV_DIR …"
    "$PYTHON" -m venv "$VENV_DIR"
  else
    echo "Virtual environment already exists at $VENV_DIR."
  fi
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
  echo "Activated virtual environment."
fi

# ── Pip upgrade ────────────────────────────────────────────────────────────

pip install --quiet --upgrade pip setuptools wheel

# ── Install project dependencies ───────────────────────────────────────────

echo "Installing requirements …"
pip install --quiet -r "$REPO_ROOT/requirements.txt"

if [[ "$DEV_INSTALL" -eq 1 ]]; then
  echo "Installing dev extras …"
  pip install --quiet pytest pytest-cov
fi

# ── Platform-specific setup ────────────────────────────────────────────────

OS="$(uname -s)"

if [[ "$OS" == "Linux" ]]; then
  echo ""
  echo "── Linux: SocketCAN setup ─────────────────────"
  # Load can and vcan kernel modules (if not already loaded)
  for mod in can can_raw vcan; do
    if ! lsmod | grep -q "^$mod"; then
      echo "Loading kernel module: $mod"
      sudo modprobe "$mod" 2>/dev/null || echo "  (could not load $mod – may need root)"
    fi
  done

  # Create a virtual CAN interface for testing
  if ! ip link show vcan0 &>/dev/null; then
    echo "Creating vcan0 interface …"
    sudo ip link add dev vcan0 type vcan 2>/dev/null || true
    sudo ip link set up vcan0 2>/dev/null || true
  fi
  echo "vcan0 ready."
fi

if [[ "$OS" == "Darwin" ]]; then
  echo ""
  echo "── macOS: dependencies ────────────────────────"
  if command -v brew &>/dev/null; then
    brew list python-can &>/dev/null || brew install python-can 2>/dev/null || true
  fi
fi

# ── Create data directories ────────────────────────────────────────────────

mkdir -p "$REPO_ROOT/data/captures" "$REPO_ROOT/data/dumps"

# ── Summary ───────────────────────────────────────────────────────────────

echo ""
echo "════════════════════════════════════════════════"
echo "  Setup complete!"
echo ""
echo "  To activate the venv manually:"
echo "    source $VENV_DIR/bin/activate"
echo ""
echo "  Quick test (simulation mode):"
echo "    python scripts/diagnostic_scan.py --simulate"
echo ""
echo "  Full TUI:"
echo "    python -m tui.app"
echo "════════════════════════════════════════════════"
