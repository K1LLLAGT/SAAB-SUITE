# SAAB_SUITE — Authoritative CAN/UDS Migration (ports-aligned)

This supersedes the `interface.py`-centric advice in the earlier `MIGRATION.md`.
Now that the real `ports/` and `domain/` are visible, the correct direction is
to **retire the legacy `interface.py` / `remote_interface.py` stack onto the
hexagonal ports you already built** — not to consolidate into `interface.py`.

All code referenced here was tested end-to-end against stand-ins for your real
`ICanSource`, `ICanSink`, `IIsoTpTransport`, `CanBus`, and `domain.can.frame.CanFrame`.

---

## Corrected understanding of the repo

Two parallel CAN stacks exist:

| | Legacy (working) | Hexagonal (intended, mostly stubs) |
|---|---|---|
| Frame | `adapters/can/interface.CanFrame` + a duplicate in `remote_interface` | `domain/can/frame.CanFrame` (validated, FD-aware, provenanced) |
| RX | `CanInterface.recv` / `RemoteCanInterface.recv` | `ports.can_source.ICanSource.read` |
| TX | `.send` | `ports.can_sink.ICanSink.write` |
| ISO-TP | inlined in `uds_client` | `ports.isotp.IIsoTpTransport` |
| UDS | concrete `uds_client.UdsClient` | `ports.uds.IUdsClient` |
| Backends | `CanInterface` (python-can) | `*_source.py` Phase-2 `NotImplementedError` stubs |

The ports + domain layer is the better design and is nearly complete. The job is
to fill the adapters and cut the legacy stack over.

## Canonical decisions

1. **One frame: `domain.can.frame.CanFrame`.** Used both directions —
   `ICanSink.write` and `ICanSource.read` both speak it. Delete the `CanFrame`
   in `interface.py` and `remote_interface.py`.
2. **`is_extended` is explicit on the domain frame** (validated). The
   auto-detect trick from the earlier `interface.py` is a legacy-only crutch;
   drop it on the clean path — callers/addressing set `is_extended`.
3. **ISO-TP framing lives behind `IIsoTpTransport`**, not in the UDS client.
4. **The UDS client is thin** and returns raw `WirePayload`; it does not parse.

## Target file placement

```
adapters/
├── can/
│   ├── pycan_backend.py   # NEW: PyCanBackend implements ICanSource + ICanSink
│   │                      #   -> realizes socketcan_source AND canusb_source
│   ├── j2534_source.py    # keep: real J2534 backend (not python-can)
│   ├── mock_source.py     # keep
│   ├── replay_source.py   # keep (read-only ICanSource)
│   ├── socketcan_source.py# DELETE if thin (PyCanBackend covers it)
│   ├── canusb_source.py   # DELETE if thin (PyCanBackend covers it, interface="slcan")
│   ├── interface.py       # DELETE after cutover (legacy)
│   └── remote_interface.py# port its TCP logic into a PyCanBackend-style ICanSource+ICanSink, then delete
├── isotp/
│   └── transport.py       # NEW: IsoTpTransport implements IIsoTpTransport over source+sink
└── uds/
    └── client.py          # NEW: thin UdsClient implements IUdsClient over IIsoTpTransport
```

## Why socketcan + canusb collapse into one backend

`PyCanBackend` takes a python-can `interface` selector. `interface="socketcan"`
and `interface="slcan"` (LAWICEL/CANUSB) are both python-can transports, so one
class covers both — pick via runtime config. `j2534_source` stays separate
because J2534 is a vendor pass-thru DLL, not a python-can transport.

## Migration order (each step leaves the repo working)

0. **Clean cruft** — run the earlier `cleanup.sh` (`.bak`, `.bak.bak`, tracked `__pycache__`).
1. **Add the new adapters** — drop in `isotp/transport.py`, `uds/client.py`,
   `can/pycan_backend.py`. They depend only on existing ports/domain; nothing
   else imports them yet, so this is additive and safe.
2. **Wire a composition root** — somewhere (CLI / service factory) build:
   ```python
   backend = PyCanBackend(channel=cfg.channel, interface=cfg.bustype)
   backend.open(bus, cfg.bitrate)
   transport = IsoTpTransport(source=backend, sink=backend, bus=bus)
   transport.open(addresses)          # CanAddressPair for the target ECU
   uds = UdsClient(transport)
   ```
3. **Cut callers over** from the legacy `uds_client` to the new `UdsClient`.
4. **Delete legacy** — `interface.py`, `remote_interface.py`, and the two thin
   `*_source.py` once nothing imports them. `git mv`/`git rm` so history follows.

## Two assumptions to confirm (isolated, easy to fix)

1. **`CanAddressPair` shape.** `IsoTpTransport.open()` reads
   `addresses.request.can_id`, `addresses.response.can_id`, and
   `addresses.request.is_extended`. If `domain/ecu/address.py` names these
   differently, edit only that one method.
2. **`WirePayload` / `MonotonicNs`.** Treated as `bytes` / `int` NewTypes.
   If they're richer, adjust the `cast`s.

Both are confined to clearly-commented spots in `transport.py`.

## Verification

```bash
# one CanFrame everywhere
python -c "from saab_suite.domain.can.frame import CanFrame as A; \
           import saab_suite.adapters.can as can; \
           assert not hasattr(can, 'CanFrame') or can.CanFrame is A"
pytest -q
ruff check src/saab_suite/adapters
```

The end-to-end behaviour (multi-frame VIN, single-frame reads, session control,
tester-present, negative-response passthrough) is already proven against the
real port signatures; once `PyCanBackend` is pointed at your Mongoose/J2534 or a
SocketCAN device, the same `UdsClient` path runs on the car.
