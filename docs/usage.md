# Usage Guide

## Interactive interfaces

### Rich UI (menu-driven)

```bash
python -m ui.app                        # or: saab-suite (if installed)
python -m ui.app --interface socketcan --channel can0
python -m ui.app --interface j2534 --protocol ISO15765
```

Keyboard navigation: type the option number and press Enter.

### Textual TUI (full-screen)

```bash
python -m tui.app                       # or: saab-tui (if installed)
python -m tui.app --interface socketcan
```

| Key    | Action                   |
|--------|--------------------------|
| F1     | Connect to interface     |
| F2     | Discover ECUs            |
| F3     | Read DTCs                |
| F4     | Clear DTCs               |
| F5     | Refresh live data        |
| Ctrl+C | Quit                     |

---

## CLI: diagnostic_scan.py

```bash
# Basic scan (J2534, exports HTML report)
python scripts/diagnostic_scan.py --report report.html

# SocketCAN interface
python scripts/diagnostic_scan.py --interface socketcan --channel can0

# Simulation mode (no hardware)
python scripts/diagnostic_scan.py --simulate --report /tmp/report.html

# Capture CAN traffic during scan
python scripts/diagnostic_scan.py --capture traffic.csv --capture-duration 30

# JSON export
python scripts/diagnostic_scan.py --report scan.json

# Verbose output
python scripts/diagnostic_scan.py --simulate -v
```

### All options

```
usage: diagnostic_scan.py [-h] [--interface INTERFACE] [--channel CHANNEL]
                           [--protocol PROTOCOL] [--baudrate BAUDRATE]
                           [--timeout TIMEOUT] [--report REPORT]
                           [--capture CAPTURE] [--capture-duration CAPTURE_DURATION]
                           [--simulate] [-v]

options:
  --interface   Interface type: j2534, socketcan, kvaser, peak, vector (default: j2534)
  --channel     Channel identifier (default: can0)
  --protocol    Diagnostic protocol: ISO15765 or ISO14230 (default: ISO15765)
  --baudrate    CAN bus baudrate in bps (default: 500000)
  --timeout     ECU discovery timeout in seconds (default: 5)
  --report      Export report path (.json or .html)
  --capture     Capture raw CAN traffic to CSV
  --simulate    Simulation mode (no hardware needed)
  -v            Verbose output
```

---

## Python API

### Quick diagnostic scan

```python
from engine.core import DiagnosticEngine

with DiagnosticEngine(interface="j2534") as engine:
    ecus = engine.discover_ecus()
    for ecu in ecus:
        dtcs = engine.read_dtcs(ecu)
        print(f"{ecu}: {len(dtcs)} DTC(s)")
        for dtc in dtcs:
            print(f"  {dtc}")
```

### Read live data (PIDs)

```python
with DiagnosticEngine() as engine:
    ecus = engine.discover_ecus()
    ecm = ecus[0]
    rpm_raw = engine.read_pid(ecm, 0x0C)     # OBD-II PID 0x0C: engine RPM
    if rpm_raw:
        rpm = (rpm_raw[2] * 256 + rpm_raw[3]) / 4.0 if len(rpm_raw) >= 4 else rpm_raw[2] * 0.25
        print(f"RPM: {rpm:.0f}")
```

### SPS flash

```python
from sps.workflow import SPSWorkflow

with DiagnosticEngine() as engine:
    ecus = engine.discover_ecus()
    ecm  = next(e for e in ecus if "ECM" in e.name)
    wf   = SPSWorkflow(engine, ecm, calibration_path="firmware/my_cal.cce")
    result = wf.run()
    print(result)
```

### CAN capture and analysis

```python
from can.bus import CANBus
from analysis.analyzer import CANAnalyzer

# Capture
with CANBus(interface="socketcan", channel="can0") as bus:
    frames = bus.capture(duration=30, output_path="capture.csv")

# Analyse
analyser = CANAnalyzer(frames)
print(analyser.protocol_summary())
for stat in analyser.top_ids(10):
    print(stat.to_dict())
```

### Export a diagnostic report

```python
from analysis.analyzer import DiagnosticReport

report = DiagnosticReport(vin="YS3EB49S341001234", ecus=ecus, dtcs=dtcs)
report.export_html("report.html")
report.export_json("report.json")
print(report.summary())
```
