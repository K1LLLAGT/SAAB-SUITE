#!/usr/bin/env bash
# Print a one-page diagnostic of the host environment.
set -euo pipefail
echo "=== saab-suite host diagnostic ==="
echo "uname:       $(uname -a)"
echo "python:      $(python3 --version 2>&1)"
echo "pip:         $(pip --version 2>&1)"
echo "git:         $(git --version 2>&1 || echo 'not installed')"
echo "cargo:       $(cargo --version 2>&1 || echo 'not installed')"
echo "termux:      ${TERMUX_VERSION:-not termux}"
echo "in-venv:     ${VIRTUAL_ENV:-no}"
