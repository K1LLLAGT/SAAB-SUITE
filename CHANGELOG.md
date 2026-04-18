# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Initial scaffolding of the redesigned architecture (Phase 0).
- Hexagonal layering with `kernel` / `domain` / `ports` / `services` / `adapters` / `interfaces`.
- `pyproject.toml` with PEP 621 metadata, Hatchling build, and `import-linter` contracts.
- CI workflows: `ci.yml`, `release.yml`, `nightly.yml`.
- Migration script (`tools/migrate_legacy.py`) for converting the legacy tree.
- Vendor README documenting required external artifacts.

### Notes
- This release contains no business logic. All services and adapters are stubs.
- See `docs/history/phase1.md` for the legacy Phase-1 prototype.

## [0.1.0] -- Scaffolding

First scaffolding tag.
