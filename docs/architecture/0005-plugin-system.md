# ADR-0005 -- Plugin System

**Status:** Accepted

## Mechanism

Plugins are independent Python distributions registering against entry points.

```toml
[project.entry-points."saab_suite.can_source"]
vector_xl = "saab_suite_vector:VectorCanSource"

[project.entry-points."saab_suite.flash_target"]
trionic_t8 = "saab_suite_trionic:TrionicT8FlashTarget"
```

`plugins/loader.py` discovers entry points at startup, validates each against
the corresponding `Protocol`, and registers into `plugins/registry.py`.

## First-party plugins

- `saab-suite-trionic` -- Trionic T7/T8 flash targets, tuning screens
- `saab-suite-haldex`  -- Gen4 Haldex models, predictive failure
- `saab-suite-af40`    -- AF40-6 transmission diagnostics

## Contract guarantees

- Plugins see only `saab_suite.domain`, `saab_suite.ports`, `saab_suite.plugins.contracts`.
- Plugins **must not** import `saab_suite.adapters` or `saab_suite.interfaces`.
- Plugins declare `requires-saab-suite = ">=1.0,<2.0"` and are version-checked at load.
