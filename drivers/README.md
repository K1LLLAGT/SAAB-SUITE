# Drivers

This directory contains driver installation guides and helper utilities for
the interface hardware supported by SAAB-SUITE.

## Supported interfaces

### J2534 pass-through devices

| Device                       | Vendor      | Notes                                     |
|------------------------------|-------------|-------------------------------------------|
| GM MDI / MDI2                | GM / Bosch  | Recommended for GDS2/Tech2Win             |
| Drew Technologies MongoosePro GM II | Drew Tech | Excellent SAAB/GM support         |
| Bosch KTS 590/560            | Bosch       | High-quality, expensive                   |
| OBDLINK SX/EX                | OBDLink     | Budget option, limited protocols          |
| Tactrix Openport 2.0         | Tactrix     | Good for reflashing                       |

### SocketCAN / Linux

```bash
# Load the CAN kernel modules
sudo modprobe can can_raw vcan

# Bring up a physical CAN interface (example: Peak PCAN-USB)
sudo modprobe peak_usb
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0

# Virtual CAN for testing
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Windows (J2534 DLL)

1. Install the manufacturer's driver (e.g. `MDI2Setup.exe`).
2. The DLL path is automatically registered in the Windows registry under
   `HKLM\SOFTWARE\PassThruSupport.04.04\<device_name>`.
3. SAAB-SUITE will auto-detect the DLL on startup.

### macOS

SocketCAN is not natively supported on macOS.  Use a J2534 device with the
appropriate macOS driver, or run SAAB-SUITE inside a Linux VM.

## Python dependencies

```
pip install python-can
```

## Troubleshooting

| Symptom                        | Likely cause                 | Fix                                   |
|--------------------------------|------------------------------|---------------------------------------|
| `ERR_DEVICE_NOT_CONNECTED`     | Hardware not plugged in      | Check USB cable / power               |
| `ERR_INVALID_BAUDRATE`         | Wrong bitrate configured     | Use `--baudrate 500000` for SAAB/GM   |
| `No CAN interface found`       | Kernel module not loaded     | `sudo modprobe can_raw`               |
| `permission denied /dev/can0`  | User not in `dialout` group  | `sudo usermod -aG dialout $USER`      |
