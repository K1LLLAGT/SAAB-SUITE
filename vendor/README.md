# vendor/

Third-party artifacts required for full functionality. Not bundled with the
suite source tree.

## What goes here

| Path                          | Contents                                           | Bundled? |
|-------------------------------|----------------------------------------------------|----------|
| `drivers/j2534/`              | J2534 PassThru DLL installers                      | No       |
| `drivers/canusb/`             | LAWICEL / CANUSB CDM drivers                       | No       |
| `drivers/tech2/`              | Tech2 USB drivers                                  | No       |
| `isos/gds2/`                  | GDS2 ISO / installer                               | No       |
| `isos/tech2win/`              | Tech2Win ISO / installer                           | No       |
| `isos/globaltis/`             | GlobalTIS ISO / installer                          | No       |
| `isos/wis/`                   | Workshop Information System                        | No       |
| `isos/epc/`                   | Electronic Parts Catalog                           | No       |
| `firmware/nao_148/`           | NAO_148 GDS2 firmware drop                         | No       |
| `firmware/nao_149/`           | NAO_149 GDS2 firmware drop                         | No       |
| `firmware/tech2win_pcmcia/`   | Tech2Win PCMCIA card images                        | No       |
| `firmware/china/`             | China-market firmware variants                     | No       |
| `firmware/custom/`            | Custom / community calibrations                    | No       |
| `deliverables/`               | GDS2 XML + zipped image deliverables (active set)  | No       |
| `tools/j2534_toolbox/`        | J2534 Toolbox 3                                    | No       |
| `tools/globaltis_keygen/`     | LOCAL ONLY -- never committed (see SECURITY.md)    | No       |
| `tools/bdm/`                  | BDM tooling                                        | No       |
| `tools/card_writer/`          | CardWriter utilities                               | No       |
| `tools/memory_card_explorer/` | MemoryCardExplorer                                 | No       |
| `legacy_archive/`             | Frozen reference copies from Phase-1 migration     | No       |

## Why not bundled

1. **Licensing** -- GDS2, Tech2Win, GlobalTIS, WIS, EPC, and J2534 vendor
   drivers each have their own license terms.
2. **Size** -- ISOs and firmware drops are gigabytes.
3. **Provenance** -- the suite must be installable and testable without
   any third-party artifact.

## Git LFS

When you do place artifacts here, `.gitattributes` routes them to Git LFS.
Run `git lfs install` once on your machine before committing.

## Configuration

After placing artifacts, point the suite at them:

```toml
# ~/.config/saab-suite/config.toml
[vendor]
gds2_path = "/path/to/gds2"
tech2win_path = "/path/to/tech2win"
j2534_dll = "/path/to/MongoosePro.dll"
j2534_dll_sha256 = "abc123..."
```
