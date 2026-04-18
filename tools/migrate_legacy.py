#!/usr/bin/env python3
"""Legacy tree migration script.

Migrates the legacy ``~/SAAB-DIAGNOSTIC-AND-TUNE`` Phase-1 prototype tree
into the new layout. Operation is COPY (never move) so the legacy tree is
preserved as a safety net.

Mapping per ADR-MASTER-001 Section 4:

    Legacy path                              -> New path
    -------------------------------------------------------------------
    App/Core/j2534_lib.py                   -> archived (rewritten)
    App/Core/streaming_engine.py            -> services/live/streaming_engine.py
    App/Core/dtc_reader.py                  -> services/diagnostics/dtc_reader.py
    App/Core/vin_decoder.py                 -> services/vin/decoder.py
    App/Core/boost_model.py                 -> services/models/boost_model.py
    App/Core/torque_model.py                -> services/models/torque_model.py
    App/Core/haldex_model.py                -> services/models/haldex_model.py
    App/Core/calibration_validator.py       -> services/sps/plan_validator.py
    App/SPS/                                -> services/sps/
    App/Integrations/                       -> services/integrations/
    App/UI/                                 -> interfaces/tui/screens/
    App/Web/                                -> interfaces/web/
    App/Scripts/                            -> tools/
    Data/dbc/saab_93_95.dbc                 -> src/saab_suite/data/dbc/
    Data/firmware/                          -> vendor/firmware/
    Tools/                                  -> vendor/tools/
    Vendor_Diag_Suite/Win7-SAAB-VM/         -> vms/win7-saab/ (read-only refs)

Existing destinations are NEVER overwritten unless --force is passed.
A migration report is written to ``MIGRATION_REPORT.md`` in the destination.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

MAPPING: list[tuple[str, str]] = [
    ("App/Core/streaming_engine.py", "src/saab_suite/services/live/streaming_engine.py"),
    ("App/Core/dtc_reader.py", "src/saab_suite/services/diagnostics/dtc_reader.py"),
    ("App/Core/vin_decoder.py", "src/saab_suite/services/vin/decoder.py"),
    ("App/Core/boost_model.py", "src/saab_suite/services/models/boost_model.py"),
    ("App/Core/torque_model.py", "src/saab_suite/services/models/torque_model.py"),
    ("App/Core/haldex_model.py", "src/saab_suite/services/models/haldex_model.py"),
    ("App/Core/calibration_validator.py", "src/saab_suite/services/sps/plan_validator.py"),
    ("App/Core/j2534_lib.py", "vendor/legacy_archive/j2534_lib.py.txt"),
    ("App/SPS/", "src/saab_suite/services/sps/_legacy/"),
    ("App/Integrations/", "src/saab_suite/services/integrations/_legacy/"),
    ("App/UI/", "src/saab_suite/interfaces/tui/_legacy/"),
    ("App/Web/", "src/saab_suite/interfaces/web/_legacy/"),
    ("App/Scripts/", "tools/_legacy/"),
    ("Data/dbc/saab_93_95.dbc", "src/saab_suite/data/dbc/saab_93_95.dbc"),
    ("Data/firmware/", "vendor/firmware/legacy/"),
    ("Tools/", "vendor/tools/legacy/"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, help="Path to legacy ~/SAAB-DIAGNOSTIC-AND-TUNE tree")
    parser.add_argument("--dest", required=True, help="Path to new saab-suite tree (must already exist)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing destination paths")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan; copy nothing")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    dest = Path(args.dest).expanduser().resolve()

    if not source.is_dir():
        print(f"ERROR: source {source} is not a directory", file=sys.stderr)
        return 1
    if not dest.is_dir():
        print(f"ERROR: dest {dest} is not a directory (run scaffolding generator first)", file=sys.stderr)
        return 1

    report_lines = ["# Legacy migration report", ""]
    copied = 0
    skipped = 0
    missing = 0

    for src_rel, dst_rel in MAPPING:
        src = source / src_rel
        dst = dest / dst_rel
        if not src.exists():
            report_lines.append(f"- MISSING: `{src_rel}` (not present in legacy tree)")
            missing += 1
            continue
        if dst.exists() and not args.force:
            report_lines.append(f"- SKIP: `{src_rel}` (destination `{dst_rel}` exists, use --force)")
            skipped += 1
            continue
        report_lines.append(f"- COPY: `{src_rel}` -> `{dst_rel}`")
        if args.dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied += 1

    report = dest / "MIGRATION_REPORT.md"
    if not args.dry_run:
        report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"copied={copied} skipped={skipped} missing={missing}")
    print(f"report: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
