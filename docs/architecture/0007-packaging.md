# ADR-0007 -- Packaging

**Status:** Accepted

## Single source, multiple targets

`pyproject.toml` is canonical. Build artifacts:

| Target           | Tool        | Output                                   |
|------------------|-------------|------------------------------------------|
| Wheel + sdist    | hatchling   | `dist/saab_suite-*-py3-none-any.whl`     |
| AppImage (Linux) | linuxdeploy | `SAAB-Suite-*-x86_64.AppImage`           |
| Termux (Android) | shell       | `packaging/termux/install.sh`            |
| Windows (VM)     | Inno Setup  | `SAAB-Suite-*-windows-companion.exe`     |
| Docker           | docker      | `saab-suite:runtime` / `saab-suite:dev`  |

## Versioning

SemVer with calver suffix on releases (`1.4.0+2026.04`). Pre-1.0 only during
initial migration.

## Hardware extras

Hardware adapters are opt-in via `[hardware]`. Wheel installs cleanly on any
platform without DLLs.
