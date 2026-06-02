# SAAB Suite

A modern, modular diagnostic and flashing environment for SAAB 9‑3 / 9‑5 vehicles.

SAAB Suite provides:

- CAN bus communication (mock, virtual, remote TCP)
- UDS & KWP2000 diagnostics
- Tech2 emulator (Phase‑2)
- SPS‑style flashing workflows
- Calibration & firmware management
- CAN replay, logging, and analysis
- Pure Python 3.13 support on Termux/Android, Linux, and Windows

The project targets OEM‑grade reliability, a clean ports‑and‑adapters architecture, and easy extensibility.

---

## ✨ Features

- **`RemoteTcpBus`** — custom TCP CAN transport
- **Pure‑Python stack** — no Rust, no native wheels
- **`src/` layout** — modern, maintainable project structure
- **Adapters** for CAN, ISO‑TP, UDS, KWP2000, J2534
- **Domain models** for ECUs, DTCs, calibration, firmware
- **Runtime config system** (TOML)
- **Replay engine** for CAN logs
- **Mock mode** for offline development

---

## ⚠️ ECU & workflow coverage

SAAB Suite spans two generations of SAAB electronics. Pick the workflow that matches your car's ECU family.

| Workflow            | ECU family                  | Typical vehicles                     | Flash path           |
|---------------------|-----------------------------|--------------------------------------|----------------------|
| Tech2 emulator      | Trionic T5 / T7 / T8        | 9‑3 (Trionic), 9‑5 (Trionic)         | SPS / Trionic        |
| SPS flashing        | GM Global A / Trionic       | GM‑platform 9‑3 (2003+), 9‑5         | SPS / GM Global      |
| UDS diagnostics     | Bosch ME9.x, ME7.x, T8      | 9‑3 XWD Aero (B284R / ME9.6), etc.   | GM Global (ME9.x)    |

> **9‑3 XWD Aero (B284R):** the engine ECU is **Bosch ME9.6**, not Trionic T8. Use the **UDS** path and **GM Global** flashing — the Tech2/Trionic workflows do not apply to ME9.6.

---

## 📦 Installation

### Termux / Android

```bash
pkg update
pkg install python git
git clone https://github.com/K1LLLAGT/saab-suite.git
cd saab-suite
python3 -m venv .venv
. .venv/bin/activate
pip install python-can
pip install -e .
```

### Linux

```bash
git clone https://github.com/K1LLLAGT/saab-suite.git
cd saab-suite
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

### Windows (PowerShell)

```powershell
git clone https://github.com/K1LLLAGT/saab-suite.git
cd saab-suite
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

---

## ⚙️ Configuration

Create the config file at the platform config path:

- **Linux / Termux:** `~/.config/saab-suite/can.toml`
- **Windows:** `%APPDATA%\saab-suite\can.toml`

```toml
mode = "remote"            # mock | virtual | remote
remote_host = "192.168.1.50"
remote_port = 5000
virtual_channel = "vcan0"
```

---

## 🚗 Quick Start

```python
from saab_suite.adapters.can.remote_interface import RemoteCanInterface, CanFrame

iface = RemoteCanInterface()
iface.open()
print("CAN ready")

# Send a frame
iface.send(CanFrame(0x7E0, b"\x01\x00"))

# Receive a frame (1.0s timeout)
print(iface.recv(1.0))
```

### UDS

```python
from saab_suite.diag.uds.client import UdsClient

uds = UdsClient()
print(uds.read_data_by_identifier(0xF190))  # VIN
```

> Module paths (`remote_interface`, `remote_tcp_bus`) follow snake_case; confirm against your source tree if you renamed modules.

---

## 🧩 Directory structure

```text
saab-suite/
├── src/saab_suite/
│   ├── adapters/        # CAN, UDS, ISO-TP, J2534, replay
│   ├── domain/          # Vehicle, ECU, DTC, calibration
│   ├── kernel/          # Core types + errors
│   ├── ports/           # Interfaces
│   ├── runtime/         # Config + paths
│   ├── remote_tcp_bus.py
│   └── ...
├── tools/
├── vendor/
├── docs/
└── tests/
```

---

## 🧪 Self‑test

```python
from saab_suite.adapters.can.remote_interface import RemoteCanInterface, CanFrame

iface = RemoteCanInterface()
iface.open()
iface.send(CanFrame(0x7E0, b"\x01\x00"))
print(iface.recv(1.0))
```

---

## 📚 Documentation

Full docs are built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/):

```bash
pip install mkdocs-material
mkdocs serve     # live preview at http://127.0.0.1:8000
mkdocs build     # static site in site/
```

See the [Developer Guide](docs/developer/architecture.md) for architecture, adapters, and contribution workflow.

---

## 🛠️ Development

```bash
pip install -e .
pip install pytest ruff mypy
pytest -q          # run tests
ruff check .       # lint
mypy src/          # type-check
```

---

## 📄 License

MIT © K1LLLAGT
