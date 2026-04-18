# Phase-1 prototype (legacy)

This document archives the Phase-1 prototype that lived under
`~/SAAB-DIAGNOSTIC-AND-TUNE`. The Phase-2 redesign supersedes it.

Original components:
- `App/Core/` -- flat namespace of CAN, J2534, models, parsers, validators
- `App/SPS/` -- workflow, precheck, executor, session logger
- `App/Integrations/` -- GDS2 / Tech2Win parsers and watchers
- `App/UI/` -- TUI modules + sidebar/status panels
- `App/Web/` -- Flask routes + Jinja templates
- `App/Scripts/` -- analysis scripts and PowerShell VM helpers

See `docs/architecture/0001-hexagonal-architecture.md` for the rationale and
`tools/migrate_legacy.py` for the conversion script.
