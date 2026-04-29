# Installation

## Prerequisites

| Requirement         | Minimum version | Notes                              |
|---------------------|-----------------|------------------------------------|
| Python              | 3.10            | 3.11+ recommended                  |
| pip                 | 22.0            |                                    |
| python-can          | 4.3.0           | For SocketCAN / Kvaser / PEAK      |
| rich                | 13.7.0          | Required for the Rich UI           |
| textual             | 0.47.0          | Required for the full-screen TUI   |
| numpy / pandas      | ≥1.26 / ≥2.2    | Required for data analysis         |
| matplotlib          | ≥3.8.0          | Optional, required for PID plots   |

## Install from source

```bash
# 1. Clone the repository
git clone https://github.com/K1LLLAGT/SAAB-SUITE.git
cd SAAB-SUITE

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate.bat       # Windows CMD
# .venv\Scripts\Activate.ps1       # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) install SAAB-SUITE as a package for CLI entry-points
pip install -e .
```

Or use the automated setup script:

```bash
./scripts/setup.sh           # Linux / macOS
./scripts/setup.sh --dev     # Also install test extras
```

## Verify the installation

```bash
# Run the unit tests
pytest tests/ -v

# Smoke test (simulation mode, no hardware needed)
python scripts/diagnostic_scan.py --simulate
```

## Platform notes

### Linux

```bash
# Allow your user to access CAN interfaces without sudo
sudo usermod -aG dialout $USER
newgrp dialout

# Load kernel modules
sudo modprobe can can_raw
```

### Windows

1. Install a J2534-compatible driver (e.g. GM MDI software suite).
2. Verify the DLL is registered:
   `HKLM\SOFTWARE\PassThruSupport.04.04\<device_name> → FunctionLibrary`
3. Run SAAB-SUITE from an administrator prompt if access is denied.

### macOS

python-can supports socketcan via a USB-CAN adapter (e.g. PEAK PCAN-USB with
macOS driver).  J2534 DLLs are not directly supported on macOS; use VMware
Fusion running Windows for full J2534 functionality.

## Uninstall

```bash
pip uninstall saab-suite
# Remove the virtual environment
rm -rf .venv
```
