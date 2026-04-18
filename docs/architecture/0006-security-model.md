# ADR-0006 -- Security Model

**Status:** Accepted

See `SECURITY.md` for the user-facing summary.

## Defense in depth for real flash

Six independent gates. Removing any is a breaking change.

1. Plan validation produces a token.
2. `--confirm=<token>` must match.
3. `SAAB_SUITE_ENABLE_REAL_FLASH=1` must be set.
4. Audit log must be healthy.
5. Exclusive bus lock must be acquired.
6. Precheck must pass.

## Audit log

Append-only SQLite with hash chain in `runtime/audit/audit.sqlite`. Each
event carries `prev_hash` + `hash`. Any tamper breaks the chain.

## Per-session JSONL

Human-readable session log at `runtime/logs/sessions/sps/<vin>/<utc>.jsonl`.
Both audit DB and JSONL are written; they cross-validate.
