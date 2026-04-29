# VM Environments

This directory documents the virtual machine configurations used by SAAB-SUITE
for running GDS2 and Tech2Win, which require Windows environments.

## Overview

| VM Image               | Purpose                         | Hypervisor        |
|------------------------|---------------------------------|-------------------|
| `tech2win.vmx`         | Tech2Win (SAAB Tech2 emulator)  | VMware Workstation/Fusion |
| `gds2.vmx`             | GDS2 (optional isolated install)| VMware Workstation/Fusion |

## Tech2Win setup

Tech2Win emulates a GM Tech2 scan tool on a Windows PC.  It requires:

1. **VMware Workstation** (Windows/Linux) or **VMware Fusion** (macOS).
2. A licensed copy of Tech2Win obtained from a GM dealer subscription.
3. A compatible J2534 device (see [drivers/README.md](../drivers/README.md)).

### VM USB pass-through

Configure your J2534 device to be passed through to the VM:

```
VM Settings → USB Controller → Add → select your J2534 device
```

### SAAB-SUITE Tech2Win bridge

```python
from gds2.integration import Tech2WinBridge

bridge = Tech2WinBridge(vm_path="vm/tech2win.vmx", j2534_device="GM MDI")
bridge.start_vm()
# ... use Tech2Win for diagnostics ...
bridge.stop_vm()
```

Or via the CLI:

```bash
# From the interactive TUI (option T)
saab-tui

# Or directly
python -c "from gds2.integration import Tech2WinBridge; Tech2WinBridge().start_vm()"
```

## GDS2 setup

GDS2 (Global Diagnostic System 2) is GM's current dealer tool.  It can run
natively on Windows without a VM.  See [../docs/gds2_setup.md](../docs/gds2_setup.md)
for full installation instructions.

## VM image storage

VM image files (`.vmx`, `.vmdk`, `.iso`, `.ova`) are excluded from this
repository via `.gitignore` due to their large size and licensing restrictions.
Place your licensed VM images in this directory.
