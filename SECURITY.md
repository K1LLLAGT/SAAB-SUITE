# Security Policy

## Scope

Covers firmware integrity, SPS safety interlocks, audit logging, isolation
of flashing operations, and disclosure. For the architectural treatment see
`docs/architecture/0006-security-model.md`.

## Threat model summary

| Threat                                | Mitigation                                                                  |
|---------------------------------------|-----------------------------------------------------------------------------|
| Wrong calibration flashed             | Plan validator interlocks, partnumber compatibility matrix, signed manifest |
| Tampered firmware image               | SHA256 + manifest signature verified pre-`TransferData`                     |
| Replay attack on flash session        | Ephemeral `flash_session_id`, per-session SecurityAccess seed               |
| Unauthorized local API access         | 127.0.0.1 bind by default; bearer token for non-loopback                    |
| Audit log tampering                   | Append-only SQLite with hash chain                                          |
| DLL hijacking on Windows side         | J2534 DLL path resolved via registry; SHA256 pinned                         |
| Hardware unavailable mid-flash        | Recovery mode + resumable session                                           |
| Battery drop mid-flash                | Precheck minimum voltage; live monitoring with abort threshold              |
| Concurrent J2534 device access        | Process-level lock file in `runtime/locks/`                                 |
| Vendor licensing artifacts in git     | `vendor/tools/*keygen*` `.gitignored`; CI rejects matching paths            |

## Real flash safety gates (defense in depth)

To execute a real flash, **all** of the following must be true:

1. The plan must be validated (`saab sps validate`) -- produces a token.
2. The `--confirm=<token>` flag must match the validated token bit-for-bit.
3. The environment variable `SAAB_SUITE_ENABLE_REAL_FLASH=1` must be set.
4. The audit log must be healthy (chain unbroken, disk writable).
5. An exclusive bus lock must be acquirable.
6. Precheck must pass.

Removing **any** gate is a breaking change requiring a major version bump.

## Vendor licensing posture

The legacy tree contained references to `Tools/GlobalTIS/GlobalTis_Keygen.rar`.
Such artifacts are not redistributed by this project. They are `.gitignored`
under `vendor/tools/` and CI rejects PRs that add files matching `*keygen*`,
`*crack*`, or `*serial*` outside `vendor/tools/` (where they remain local-only).

If you possess legitimate licenses for GDS2, Tech2Win, GlobalTIS, WIS, or EPC,
configure their installation paths in `~/.config/saab-suite/config.toml` and
the suite will integrate with them. The suite does not bundle them.

## Reporting vulnerabilities

Contact the maintainer privately for vulnerabilities affecting flash safety,
audit log integrity, or authentication.
