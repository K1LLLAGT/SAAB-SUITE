"""Command-line interface for saab-workshop.exe.

saab-workshop extract --source D:\\SaabWorkshopSync [--manifest PATH]
saab-workshop verify
saab-workshop list
saab-workshop launch gds2
saab-workshop gui
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import WorkshopConfig
from .extractor import sync_vendor
from .launcher import TOOL_REGISTRY, launch_tool, list_available_tools
from .logging_setup import configure_logging, get_logger
from .manifest import find_latest_manifest, index_by_basename, load_manifest, sha256_of


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="saab-workshop", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser(
        "extract",
        help="sync a local vendor source into %USERPROFILE%\\SaabWorkshop\\vendor",
    )
    p_extract.add_argument(
        "--source",
        required=True,
        help="folder containing your own already-licensed OEM tools/ISOs",
    )
    p_extract.add_argument(
        "--manifest",
        help=(
            "path to a JSONL manifest "
            "(defaults to the newest one under the workshop manifests dir if omitted)"
        ),
    )
    p_extract.add_argument(
        "--include-unclassified",
        action="store_true",
        help="also copy files the classifier could not categorize",
    )

    sub.add_parser("verify", help="verify every file under vendor/ against the newest manifest")
    sub.add_parser("list", help="list OEM tools currently discoverable under vendor/")

    p_launch = sub.add_parser("launch", help="launch a tool by category")
    p_launch.add_argument("category", choices=sorted(TOOL_REGISTRY))
    p_launch.add_argument(
        "--index",
        type=int,
        default=0,
        help="which match to launch when multiple executables are found",
    )
    p_launch.add_argument(
        "--no-verify",
        action="store_true",
        help="skip manifest SHA256 verification before launch",
    )

    sub.add_parser("gui", help="launch the graphical interface")

    return parser


def _cmd_extract(config: WorkshopConfig, args: argparse.Namespace) -> int:
    manifest_path = (
        Path(args.manifest) if args.manifest else find_latest_manifest(config.manifest_dir)
    )
    result = sync_vendor(
        config,
        Path(args.source),
        manifest_path=manifest_path,
        include_unclassified=args.include_unclassified,
    )
    print(
        f"scanned={result.scanned} copied={result.copied} unchanged={result.skipped_unchanged} "
        f"hash_mismatch={result.skipped_hash_mismatch} unclassified={result.skipped_unclassified} "
        f"failed={result.failed}"
    )
    return 0 if result.failed == 0 else 1


def _cmd_verify(config: WorkshopConfig, _args: argparse.Namespace) -> int:
    manifest_path = find_latest_manifest(config.manifest_dir)
    if manifest_path is None:
        print("no manifest found; nothing to verify against")
        return 0

    index = index_by_basename(load_manifest(manifest_path))
    checked = mismatched = missing_from_disk = 0
    for entry in index.values():
        found_path = next(config.vendor_dir.glob(f"**/{entry.basename}"), None)
        if found_path is None:
            missing_from_disk += 1
            continue
        checked += 1
        actual = sha256_of(found_path)
        if actual != entry.sha256:
            mismatched += 1
            print(f"MISMATCH: {found_path} (expected {entry.sha256}, got {actual})")
    print(f"checked={checked} mismatched={mismatched} missing_from_disk={missing_from_disk}")
    return 0 if mismatched == 0 else 1


def _cmd_list(config: WorkshopConfig, _args: argparse.Namespace) -> int:
    tools = list_available_tools(config)
    for category, paths in sorted(tools.items()):
        label = TOOL_REGISTRY[category][0]
        if not paths:
            print(f"[ ] {label} ({category}): not found")
            continue
        for i, path in enumerate(paths):
            print(f"[{i}] {label} ({category}): {path}")
    return 0


def _cmd_launch(config: WorkshopConfig, args: argparse.Namespace) -> int:
    result = launch_tool(config, args.category, index=args.index, verify=not args.no_verify)
    print(result.message)
    return 0 if result.ok else 1


def _cmd_gui(_config: WorkshopConfig, _args: argparse.Namespace) -> int:
    from .gui import run_gui

    return run_gui(_config)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    config = WorkshopConfig.load()
    config.ensure_directories()
    configure_logging(config.log_dir, config.log_level)
    logger = get_logger()
    logger.info("saab-workshop starting: command=%s home=%s", args.command, config.home_dir)

    handlers = {
        "extract": _cmd_extract,
        "verify": _cmd_verify,
        "list": _cmd_list,
        "launch": _cmd_launch,
        "gui": _cmd_gui,
    }

    try:
        return handlers[args.command](config, args)
    except Exception as exc:
        logger.exception("unhandled error in command %s: %s", args.command, exc)
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
