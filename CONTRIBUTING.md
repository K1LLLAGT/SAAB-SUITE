# Contributing

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,tui,web]"
```

## Before every commit

```bash
ruff format .
ruff check . --fix
mypy src/saab_suite
lint-imports
pytest -m "not hw"
```

## Architectural rules (enforced by import-linter in CI)

1. Inward dependencies only: `interfaces -> adapters -> services -> ports -> domain -> kernel`.
2. The kernel imports nothing from the project.
3. The domain has no I/O. No `socket`, no `ctypes`, no HTTP, no file I/O.
4. Services don't know about adapters or interfaces.
5. Only `adapters/j2534/windows_dll.py` may import `ctypes`.
6. Sibling interfaces don't cross-import.

A PR that violates any of these will not merge.

## Adding a new CAN source

1. Implement `saab_suite.ports.can_source.ICanSource` in `adapters/can/<n>_source.py`.
2. Add an entry-point in `pyproject.toml` under `[project.entry-points."saab_suite.can_source"]`.
3. Add unit tests in `tests/unit/adapters/can/`.
4. Add an integration test in `tests/integration/can_stack/`.

## Adding a new ECU flash target

This is safety-critical. Read `docs/architecture/0006-security-model.md` first.

1. Implement `saab_suite.ports.flash_target.IFlashTarget` in a plugin (not core).
2. Provide a `MockFlashTarget` for the same family in `tests/fixtures/`.
3. Add hypothesis property tests for the plan validator against the new target.
4. Hardware tests are gated behind `pytest -m hw`.
