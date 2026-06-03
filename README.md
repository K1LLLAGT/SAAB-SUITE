# SAAB-SUITE

SAAB-SUITE is a hexagonally-architected diagnostic and flashing suite for Saab vehicles.

## Features
- CAN / UDS / KWP / J2534
- VIN-aware profiles
- SPS workflows
- Plugin system
- Multi-platform packaging

## Quick Start

    git clone <YOUR_REPO_URL> SAAB-SUITE
    cd SAAB-SUITE
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    saab-suite --help

## Development

    tools/format.sh
    tools/lint.sh
    tools/typecheck.sh
    tools/test.sh

## Packaging
- AppImage
- Docker
- Termux
- Windows installer
