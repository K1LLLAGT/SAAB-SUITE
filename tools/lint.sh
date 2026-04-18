#!/usr/bin/env bash
set -euo pipefail
ruff check .
lint-imports
