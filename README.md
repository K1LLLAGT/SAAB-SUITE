# SAAB-SUITE

SAAB-SUITE is a hexagonally-architected diagnostic and flashing suite for Saab vehicles.  
It supports OEM protocols, custom firmware, and multi-platform runtimes including Linux, Windows, Termux, Docker, and AppImage.

## Features

- Hexagonal architecture (adapters, domain, services, interfaces, kernel, ports)
- CAN / UDS / KWP / J2534 support
- VIN-aware vehicle profiles and SPS workflows
- Plugin system (AF40, Haldex, Trionic, etc.)
- Multi-platform packaging (AppImage, Docker, Termux, Windows installer)

## Quick Start

Clone and install:

    git clone <YOUR_REPO_URL> SAAB-SUITE
    cd SAAB-SUITE
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    saab-suite --help

## Architecture

See:

- docs/architecture/0001-hexagonal-architecture.md  
- docs/architecture/saab-suite-architecture.mmd  

## Development

    tools/format.sh
    tools/lint.sh
    tools/typecheck.sh
    tools/test.sh

## Packaging

- AppImage: packaging/appimage/build.sh
- Docker: packaging/docker/
- Termux: packaging/termux/install.sh
- Windows: packaging/windows/installer.iss

## Runtime Layout

Runtime data (logs, cache, backups, locks) is stored under:

    $HOME/.saab-suite/runtime

or a custom path via:

    export SAAB_SUITE_RUNTIME=/path/to/runtime

