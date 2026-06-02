# Developer Onboarding

## 1. Prerequisites
- Python 3.11+
- Git
- Optional: Docker
- Optional: Termux (Android)

## 2. Setup

    git clone <YOUR_REPO_URL> SAAB-SUITE
    cd SAAB-SUITE
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"

## 3. Project Layout
- src/SAAB-SUITE/ — main package
- plugins/ — plugin packages
- runtime/ — logs, cache, backups, locks
- vendor/ — drivers, firmware, ISOs, tools
- packaging/ — AppImage, Docker, Termux, Windows
- tests/ — unit, integration, system tests

## 4. Dev Commands

    tools/format.sh
    tools/lint.sh
    tools/typecheck.sh
    tools/test.sh

## 5. Adding a Plugin

    tools/new_plugin.py <name>

Then edit:
- plugins/saab-suite-<name>/pyproject.toml
- plugins/saab-suite-<name>/src/saab_suite_<name>/plugin.py
