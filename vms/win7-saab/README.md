# Win7-SAAB VM

Hosts the OEM-grade vendor diagnostic stack.

## Components installed

- GDS2 (NAO_148 + NAO_149 firmware drops)
- Tech2Win
- GlobalTIS
- J2534 Toolbox 3
- Workshop Information System (WIS) (optional)
- Electronic Parts Catalog (EPC) (optional)

## Build

```bash
cd vms/win7-saab
vagrant up
```

Requires VirtualBox 7.0+, Vagrant 2.4+, and ~50GB free disk.

## Networking

- Private network: 192.168.56.71
- Synced folder: host `vendor/` -> guest `/vendor`

## Disk image

VirtualBox `.vdi` files are .gitignored. Snapshot before any vendor install
attempt; vendor tools can be touchy and rolling back is the recovery path.
