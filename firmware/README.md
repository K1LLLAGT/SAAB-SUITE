# Firmware Packages

This directory holds ECU firmware / calibration packages for supported SAAB/GM vehicles.

## Directory layout

```
firmware/
├── saab_9-3/          # SAAB 9-3 (2003–2011, YS3F chassis)
│   ├── ecm/           # Engine Control Module calibrations
│   ├── tcm/           # Transmission Control Module
│   └── bcm/           # Body Control Module
├── saab_9-5/          # SAAB 9-5 (1998–2011, YS3E/YS3G chassis)
│   ├── ecm/
│   └── tcm/
└── README.md          # This file
```

## Calibration file formats

| Extension | Description |
|-----------|-------------|
| `.cce`    | GM/SPS calibration container (compressed) |
| `.bin`    | Raw binary flash image |
| `.hex`    | Intel HEX format |
| `.s19`    | Motorola S-record format |

## Important notices

- Firmware files are **not** included in this repository due to licensing restrictions.
- Calibration files must be obtained from an authorised GM SPS subscription or through
  the vehicle's factory service procedures.
- **Flashing incorrect firmware may permanently damage the ECU.**  Always verify the
  part number and calibration ID before programming.

## Obtaining calibration files

1. Subscribe to [GM SPS](https://www.acdelcotds.com/) (requires dealer credentials).
2. Use the SPS workflow in SAAB-SUITE: `python scripts/diagnostic_scan.py --sps`.
3. Place downloaded `.cce` files in the appropriate sub-directory.

## Usage with SAAB-SUITE

```python
from sps.workflow import SPSWorkflow
from engine.core import DiagnosticEngine, ECUInfo

with DiagnosticEngine() as engine:
    ecus = engine.discover_ecus()
    ecm  = next(e for e in ecus if "ECM" in e.name)
    wf   = SPSWorkflow(engine, ecm, calibration_path="firmware/saab_9-3/ecm/my_cal.cce")
    result = wf.run()
    print(result)
```
