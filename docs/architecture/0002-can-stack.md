# ADR-0002 -- CAN Stack

**Status:** Accepted

## Layers

```
services/live/streaming_engine.py
services/discovery/module_discovery.py
services/diagnostics/dtc_reader.py
        |
        v
ports/uds.py    ports/kwp2000.py
        |             |
        +------+------+
               v
        ports/isotp.py          (ISO 15765-2)
               |
               v
        ports/can_source.py / ports/can_sink.py
               |
               v
adapters/can/{j2534,socketcan,replay,canusb,mock}_source.py
```

## ICanSource contract (sketch)

```python
class ICanSource(Protocol):
    def open(self, bus: CanBus, bitrate: int) -> None: ...
    def close(self) -> None: ...
    def read(self, timeout_ms: int) -> CanFrame | None: ...
    def iter_frames(self) -> Iterator[CanFrame]: ...
    def filter(self, mask: CanFilter) -> None: ...
    @property
    def stats(self) -> CanSourceStats: ...
```

## J2534 isolation

`adapters/j2534/windows_dll.py` is the **only** file in the codebase that
imports `ctypes`. Enforced by import-linter.
