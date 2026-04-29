# Architecture

## Module overview

```
SAAB-SUITE/
│
├── src/
│   ├── engine/          # Core diagnostic engine
│   │   ├── core.py      # DiagnosticEngine – connection, ECU discovery, DTC/PID
│   │   └── diagnostic.py # DTCCode, DiagnosticSession, security access
│   │
│   ├── can/             # CAN bus tools
│   │   ├── bus.py       # CANBus – open/close, send/recv, capture, callbacks
│   │   └── protocols.py # ISO15765 (CAN TP), KWP2000 (K-line) codecs
│   │
│   ├── j2534/           # SAE J2534 pass-through API
│   │   └── interface.py # J2534Interface, PassThruChannel, J2534Error
│   │
│   ├── gds2/            # OEM tool integration
│   │   └── integration.py # GDS2Integration, Tech2WinBridge
│   │
│   ├── sps/             # Service Programming System
│   │   └── workflow.py  # SPSWorkflow – full UDS flash sequence
│   │
│   ├── analysis/        # Data analysis
│   │   └── analyzer.py  # CANAnalyzer, DiagnosticReport
│   │
│   ├── ui/              # Rich-based menu UI
│   │   └── app.py       # SAABSuiteApp, main()
│   │
│   └── tui/             # Textual full-screen TUI
│       └── app.py       # SAABSuiteTUI, main()
│
├── firmware/            # Calibration file storage (not shipped)
├── drivers/             # Driver guides
├── vm/                  # VM image documentation
├── docs/                # User and developer documentation
├── scripts/             # Automation scripts
│   ├── diagnostic_scan.py
│   └── setup.sh
└── tests/               # pytest test suite
```

## Dependency hierarchy

```
ui / tui
    └── engine.core ──────── j2534.interface
    │                └───── can.bus ─── can.protocols
    └── sps.workflow ─────── engine.core
    └── gds2.integration
    └── analysis.analyzer ── engine.diagnostic
```

## Design decisions

### Hardware abstraction

`DiagnosticEngine` accepts any python-can compatible bus object or a
`J2534Interface` through duck typing (the `send_uds` / `shutdown` contract).
This means the engine works the same regardless of whether it is using a
USB-CAN dongle, a J2534 pass-through box, or a `_NullBus` in unit tests.

### Graceful degradation

All modules are designed to import successfully even when optional dependencies
(python-can, rich, textual, matplotlib) are not installed.  Errors are reported
at runtime only when the missing feature is actually used.

### ISO 15765-2 implementation

The `ISO15765` codec in `can.protocols` is a pure-Python implementation of the
CAN transport layer.  It handles single-frame and multi-frame encoding and
decoding independently of the underlying bus hardware.

### SPS safety

The `SPSWorkflow` always attempts to return the ECU to the default diagnostic
session on failure (via `_attempt_recovery`).  A full implementation should
also save the original calibration before erasing, allowing rollback.
