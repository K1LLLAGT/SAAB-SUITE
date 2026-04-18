# WinXP-SAAB VM

For legacy tooling that does not run on Win7+:

- Older Tech2Win versions (PCMCIA card flow)
- BDM tooling
- Card writer utilities
- MemoryCardExplorer

## Build

```bash
cd vms/winxp-saab
vagrant up
```

## Networking

- Private network: 192.168.56.72

## Disk image

`.vdi` is .gitignored. WinXP boxes are increasingly hard to source legitimately;
keep your provisioned image as a treasured artifact and snapshot aggressively.
