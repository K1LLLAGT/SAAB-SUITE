#!/usr/bin/env bash
set -euo pipefail

find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
find . -name '*.pyo' -delete
find . -name '*.bak' -delete

echo "Cleanup complete."
