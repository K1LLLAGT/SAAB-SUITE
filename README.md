# SAAB-SUITE

> Full SAAB/GM diagnostic suite with Python engine, CAN tools, GDS2/Tech2Win integrations, SPS workflows, firmware packages, drivers, VM environments, documentation, and automation scripts. Includes UI/TUI modules, J2534 support, data analysis tools, and complete diagnostic/tuning workflows.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Features

| Module | Description |
|--------|-------------|
| **Python Engine** | Core diagnostic engine – ECU discovery, DTC read/clear, live data PIDs |
| **CAN Tools** | CANBus wrapper (python-can), ISO 15765-2 transport layer, KWP2000 codec |
| **J2534 Support** | Full SAE J2534 pass-through API wrapper (Windows DLL + simulation mode) |
| **GDS2 / Tech2Win** | Launch helpers and process bridge for GM dealer tools |
| **SPS Workflows** | Complete UDS flash sequence: session, security, erase, download, verify |
| **Data Analysis** | CAN traffic stats, anomaly detection, PID trending, CSV/JSON/HTML export |
| **Rich UI** | Menu-driven terminal application powered by `rich` |
| **Textual TUI** | Full-screen keyboard-driven TUI powered by `textual` |
| **Firmware** | Directory layout and instructions for calibration file management |
| **Drivers** | Installation guides for J2534 devices and SocketCAN |
| **VM Environments** | VMware configuration for Tech2Win and GDS2 |
| **Automation Scripts** | `diagnostic_scan.py` CLI, `setup.sh` environment installer |

---

## Supported vehicles

- **SAAB 9-3** (YS3F, 2003–2011) — B207 / B284 petrol, Z19 diesel
- **SAAB 9-5** (YS3E, 1998–2005) — B235 / B308 petrol, D308 diesel
- **SAAB 9-5** (YS3G, 2010–2011) — B284 / A28NET
- Related GM platforms: Opel Astra H, Vectra C, Zafira B, Insignia A

See [docs/supported_vehicles.md](docs/supported_vehicles.md) for the full list.

---

## Quick start

```bash
# 1. Clone and set up
git clone https://github.com/K1LLLAGT/SAAB-SUITE.git
cd SAAB-SUITE
./scripts/setup.sh

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Simulation scan (no hardware required)
python scripts/diagnostic_scan.py --simulate --report /tmp/report.html

# 4. Full interactive TUI
python -m tui.app

# 5. Run tests
pytest tests/ -v
```

---

## Repository structure

```
SAAB-SUITE/
├── src/
│   ├── engine/        # DiagnosticEngine, DTCCode, DiagnosticSession
│   ├── can/           # CANBus, ISO15765, KWP2000
│   ├── j2534/         # J2534Interface, PassThruChannel
│   ├── gds2/          # GDS2Integration, Tech2WinBridge
│   ├── sps/           # SPSWorkflow (ECU reflashing)
│   ├── analysis/      # CANAnalyzer, DiagnosticReport
│   ├── ui/            # Rich menu UI
│   └── tui/           # Textual full-screen TUI
├── firmware/          # Calibration file storage (not included)
├── drivers/           # Driver guides
├── vm/                # VM environment documentation
├── docs/              # User documentation
├── scripts/           # CLI tools and setup scripts
└── tests/             # pytest test suite
```

---

## Documentation

| Document | Link |
|----------|------|
| Installation | [docs/installation.md](docs/installation.md) |
| Usage guide | [docs/usage.md](docs/usage.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| Supported vehicles | [docs/supported_vehicles.md](docs/supported_vehicles.md) |

---

## License

MIT — see [LICENSE](LICENSE).
