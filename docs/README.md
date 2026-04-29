# SAAB-SUITE Documentation

Welcome to the SAAB-SUITE documentation.  Use the links below to navigate to
the topic you need.

## Contents

| Document                                       | Description                                              |
|------------------------------------------------|----------------------------------------------------------|
| [Installation](installation.md)               | How to install SAAB-SUITE and its dependencies           |
| [Usage](usage.md)                             | Quick-start guide and CLI reference                      |
| [Architecture](architecture.md)               | Module overview and design decisions                     |
| [GDS2 Setup](gds2_setup.md)                   | How to integrate GDS2 and Tech2Win                       |
| [SPS Programming](sps_programming.md)         | Step-by-step ECU reflashing guide                        |
| [CAN Analysis](can_analysis.md)               | Capturing and analysing CAN traffic                      |
| [Supported Vehicles](supported_vehicles.md)   | List of tested SAAB/GM platforms                         |

## Quick start (TL;DR)

```bash
# 1. Install
git clone https://github.com/K1LLLAGT/SAAB-SUITE
cd SAAB-SUITE
./scripts/setup.sh

# 2. Activate virtual environment
source .venv/bin/activate

# 3a. Interactive UI (Rich)
python -m ui.app

# 3b. Full-screen TUI (Textual)
python -m tui.app

# 3c. Quick diagnostic scan
python scripts/diagnostic_scan.py --simulate --report /tmp/report.html
```
