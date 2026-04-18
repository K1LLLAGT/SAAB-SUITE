# ADR-0003 -- SPS Stack

**Status:** Accepted
**Safety classification:** Critical

## Five-phase pipeline

1. **Precheck** -- battery, ignition, VIN match, target reachable, audit healthy.
2. **Plan build** -- VIN -> eligible deliverables -> ordered FlashPlan.
3. **Plan validate** -- interlocks; produces `ValidatedFlashPlan` (typed gate).
4. **Execute** -- FlashExecutor steps the plan with per-step timeouts.
5. **Post-flash verify** -- re-read cal ID, clear flash-induced DTCs.

## Type-system safety

```python
class FlashPlan: ...                  # constructed by plan_builder
class ValidatedFlashPlan: ...         # only producible by plan_validator

def execute(plan: ValidatedFlashPlan) -> ...:  # cannot be called with FlashPlan
    ...
```

There is no path to `FlashExecutor.execute()` that bypasses validation,
**by construction**.

## Confirm token

`saab sps validate` emits a token = `H(plan_id, vin, validator_version, env_fingerprint)`.
`saab sps flash` requires `--confirm=<token>` matching bit-for-bit.

## Recovery

Mid-flash failures emit a resumable session-id. `saab sps recover <session-id>`
resumes from the last acknowledged transfer block.
