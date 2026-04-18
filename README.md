# SAAB Programming Suite

OEM-grade diagnostic and programming suite for SAAB 9-3 / 9-5 platforms.

**Primary target:** 2008 SAAB 9-3 XWD Aero 2.8T V6 (B284R / Trionic T8 / AF40-6 / Haldex Gen4).
**Architecture:** Hexagonal (ports-and-adapters), Python >= 3.11.
**Status:** Scaffolding (Phase 0). See `docs/architecture/0001-hexagonal-architecture.md`.

## What this is

A clean redesign of the legacy `~/SAAB-DIAGNOSTIC-AND-TUNE` tree into a layered,
testable, OEM-grade software suite. The diagnostic kernel is decoupled from
hardware (J2534, SocketCAN, CANUSB), from delivery mechanisms (CLI, TUI, Web),
and from vendor tools (GDS2, Tech2Win, GlobalTIS, SPS).

## What this is not (yet)

Scaffolding only. Tree, ports, and module signatures are in place. Business
logic is stubbed (`raise NotImplementedError`) pending Phase-2 implementation.

**Do not use this against a real ECU yet.**

## Quick start

```bash
git clone <repo> saab-suite && cd saab-suite
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,tui,web]"
pytest                  # scaffolding self-tests pass
ruff check .            # clean
mypy src/saab_suite     # clean (with stubs)
lint-imports            # contracts pass
```

## Layout

```
src/saab_suite/
  kernel/       primitives, no I/O
  domain/       business objects (immutable)
  ports/        abstract interfaces (Protocols)
  services/     use cases (pure logic)
  adapters/     concrete I/O implementations
  interfaces/   CLI, TUI, Web (delivery)
  config/       layered configuration
  logging/      structlog + audit
  plugins/      entry-point discovery
  data/         packaged resources (DBC, registries, templates)
```

Dependency direction is strictly inward. Violations fail CI via `import-linter`.

## Plugins

First-party plugins live under `plugins/`:

- `saab-suite-trionic` -- Trionic T7/T8 flash targets and tuning
- `saab-suite-haldex`  -- Gen4 Haldex models, predictive failure
- `saab-suite-af40`    -- AF40-6 transmission diagnostics

## Safety

This suite can program ECUs. **Read `SECURITY.md` before enabling real flash.**
Real flash execution requires `SAAB_SUITE_ENABLE_REAL_FLASH=1` plus a per-plan
confirmation token, by design.

## License

Proprietary. See `LICENSE`.
