# SAAB-SUITE — Layout Fix & Migration Plan

Scope: clean up and standardize `src/saab_suite/adapters/can/`, then tie it into
the wider package. The goal is one obvious home for each thing, one `CanFrame`,
and one backend contract every source implements. Do it in tiers so the repo
keeps working after every step.

---

## 1. What's wrong today

Observed in `src/saab_suite/adapters/can/`:

1. **Tracked cruft.** `remote_interface.py.bak`, `remote_interface.py.bak.bak`,
   and a committed `__pycache__/`. Git history already preserves old versions;
   these only create doubt about which file is canonical.
2. **`CanFrame` defined twice.** It lives in `interface.py`, but `uds_client.py`
   imports it from `remote_interface.py`. Two classes named `CanFrame` means
   `isinstance` and `==` silently fail across modules.
3. **Mixed responsibilities in `interface.py`.** It holds both the *frame type*
   and a *concrete backend* (`CanInterface`). Fine to keep together, but the
   shared contract that every backend should satisfy isn't expressed anywhere.
4. **Inconsistent backend naming.** Five backends are `*_source.py`
   (`canusb`, `j2534`, `mock`, `replay`, `socketcan`) but the TCP backend is
   `remote_interface.py`. Pick one convention.
5. **Possibly redundant backends.** `CanInterface` already selects any
   python-can bustype from config. If `socketcan_source.py` / `canusb_source.py`
   are just thin bustype wrappers, `CanInterface` covers them. Keep them only if
   they add real backend-specific logic (e.g. J2534 almost certainly does;
   SLCAN/canusb may need custom init).
6. **Layering smell in the UDS client.** `UdsClient` constructs a concrete
   `RemoteCanInterface()` itself. It should depend on the `CanSource` contract
   and accept whichever source is injected.

---

## 2. Target layout

### Tier 1 — minimal, low-risk (recommended first)

Keep filenames; just consolidate and add the contract.

```
adapters/can/
├── __init__.py          # re-exports: CanFrame, CanSource, CanInterface,
│                        #             RemoteCanInterface, open_source()
├── interface.py         # CanFrame (the only definition) + CanSource (Protocol)
│                        #   + CanInterface (python-can backend)
├── remote_interface.py  # RemoteCanInterface; imports CanFrame from interface
├── canusb_source.py     # implements CanSource
├── j2534_source.py      # implements CanSource
├── socketcan_source.py  # implements CanSource
├── mock_source.py       # implements CanSource
└── replay_source.py     # implements CanSource
```

### Tier 2 — fuller restructure (optional, do later)

Separate the frame, the contract, and the backends.

```
adapters/can/
├── __init__.py          # public API + open_source()
├── frame.py             # CanFrame
├── base.py              # CanSource (Protocol/ABC)
├── factory.py           # open_source(cfg) -> CanSource
└── sources/
    ├── __init__.py
    ├── pycan.py         # was interface.CanInterface (socketcan/slcan/pcan)
    ├── j2534.py
    ├── mock.py
    ├── replay.py
    └── remote.py        # was remote_interface.RemoteCanInterface
```

### Where it sits in the package (target)

```
src/saab_suite/
├── kernel/        # shared types + errors (no I/O)
├── ports/         # abstract contracts (CanSource can live here instead)
├── adapters/
│   ├── can/       # ← this directory
│   ├── isotp/     # ISO-TP transport (lift the framing out of uds_client)
│   ├── uds/       # UdsClient, services
│   └── replay/
├── domain/        # Vehicle, ECU, DTC, calibration, firmware
├── flashing/      # FlashPlan + safety gates + programmer
├── runtime/       # can_config, paths
└── cli/
```

---

## 3. Migration steps

### Step 0 — clean cruft

Run `cleanup.sh` (provided), then commit. This removes the `.bak` files and the
tracked `__pycache__`, and updates `.gitignore`.

### Step 1 — one `CanFrame`

Replace `interface.py` with the provided version (adds `CanSource` and the
per-frame `is_extended_id` auto-detect). Then make `remote_interface.py` import
the frame instead of redefining it:

```python
# top of remote_interface.py — delete any local `class CanFrame` / dataclass
from saab_suite.adapters.can.interface import CanFrame
```

Do the same in every `*_source.py` that declares its own `CanFrame`.

### Step 2 — point the UDS client at the package, not a module

In `uds_client.py`:

```python
# before
from saab_suite.adapters.can.remote_interface import RemoteCanInterface, CanFrame
# after
from saab_suite.adapters.can import CanFrame, RemoteCanInterface
```

### Step 3 (optional but recommended) — inject the source

Let `UdsClient` take any `CanSource`, defaulting to the configured one:

```python
from saab_suite.adapters.can import CanSource, open_source

class UdsClient:
    def __init__(self, req_id, res_id, timeout=1.0, source: CanSource | None = None):
        self.req_id, self.res_id, self.timeout = req_id, res_id, timeout
        self._iface = source or open_source("remote")
```

Now the same client runs over mock, replay, socketcan, or remote without edits.

### Step 4 — standardize backend naming (Tier 1 done; rename in Tier 2)

If you adopt Tier 2, use `git mv` so history follows the files:

```bash
git mv src/saab_suite/adapters/can/remote_interface.py \
       src/saab_suite/adapters/can/sources/remote.py
# ...repeat per file, then fix imports and add compat re-exports in __init__.py
```

---

## 4. Factory template

`open_source()` in the provided `__init__.py` only dispatches to classes that
are known to exist (`CanInterface`, `RemoteCanInterface`). Fill in the bespoke
backends once you confirm each module's public class name:

```python
def open_source(mode=None):
    mode = (mode or "hardware").lower()
    if mode == "remote":
        return RemoteCanInterface()
    if mode in {"hardware", "socketcan", "canusb", "slcan", "pcan"}:
        return CanInterface()            # python-can picks the bustype from config
    if mode == "mock":
        return MockCanSource()           # from .mock_source import MockCanSource
    if mode == "replay":
        return ReplayCanSource()         # from .replay_source import ReplayCanSource
    if mode == "j2534":
        return J2534CanSource()          # from .j2534_source import J2534CanSource
    raise ValueError(f"unknown CAN mode: {mode!r}")
```

---

## 5. Verify after each step

```bash
python -c "from saab_suite.adapters.can import CanFrame, CanSource, CanInterface, RemoteCanInterface"
python -c "from saab_suite.adapters.can.interface import CanFrame as A; \
           from saab_suite.adapters.can.remote_interface import CanFrame as B; \
           assert A is B, 'CanFrame still duplicated'"
pytest -q
ruff check src/saab_suite/adapters/can
```

The second check is the important one — it fails loudly if any module still
defines its own `CanFrame`.

---

## 6. Open question that decides Tier 2

Do `socketcan_source.py` and `canusb_source.py` add backend-specific logic, or
are they thin wrappers around a python-can bustype? If thin, fold them into
`CanInterface` and delete them. If they do real work, keep them as `CanSource`
implementations. Send those two files (plus `j2534_source.py`) and I'll finalize
the factory with your real class names and confirm the consolidation.
