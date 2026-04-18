# ADR-0001 -- Hexagonal Architecture

**Status:** Accepted
**Date:** 2026-04
**Supersedes:** Legacy `App/Core/` flat layout

## Context

The legacy tree mixed concerns in `App/Core/`: hardware bindings (`j2534_lib.py`),
math models (`boost_model.py`), data parsers (`vin_decoder.py`), and orchestration
(`streaming_engine.py`) all in one namespace. Cross-cutting changes were risky;
tests required hardware; UI logic leaked into protocol code.

## Decision

Adopt a strict hexagonal (ports-and-adapters) architecture with six layers and
inward-only dependencies:

```
interfaces -> adapters -> services -> ports -> domain -> kernel
```

Enforced by `import-linter` contracts in `pyproject.toml`. Violations fail CI.

## Consequences

**Positive**
- Kernel and services are testable without hardware.
- Hardware adapters are swappable (J2534 / SocketCAN / replay) by config.
- VehicleProfile flows through every service via a single shape.
- Plugins extend through ports without touching core.

**Negative**
- More files than a flat layout.
- Indirection between use case and I/O.

## Alternatives considered

- **Layered MVC** -- too coupled to a single delivery mechanism.
- **Clean Architecture** -- equivalent but heavier vocabulary.
- **Service-oriented (microservices)** -- overkill for a single-user shop tool.
