#!/usr/bin/env python3
import shutil
import subprocess
from importlib import import_module

import pkg_resources


def check_imports():
    """Check Imports."""
    modules = [
        "saab_suite",
        "saab_suite.interfaces.cli.main",
        "saab_suite.services.vin.decoder",
        "saab_suite.services.sps.plan_builder",
    ]
    for m in modules:
        import_module(m)
    print("[OK] Core imports")

def check_plugins():
    """Check Plugins."""
    eps = list(pkg_resources.iter_entry_points("saab_suite.plugins"))
    print(f"[OK] {len(eps)} plugins detected")
    for ep in eps:
        ep.load()

def check_cli():
    """Check Cli."""
    saab = shutil.which("saab")
    if saab is None:
        msg = "saab entrypoint not found"
        raise RuntimeError(msg)
    subprocess.run([saab, "--help"], check=True, capture_output=True)  # noqa: S603
    subprocess.run([saab, "diag", "--help"], check=True, capture_output=True)  # noqa: S603
    print("[OK] CLI entrypoints")

def check_runtime():
    """Check Runtime."""
    from saab_suite.runtime import paths
    for p in [paths.LOG_DIR, paths.CACHE_DIR, paths.BACKUP_DIR, paths.LOCK_DIR]:
        print("[OK] Runtime path:", p)
    paths.ensure_dirs()

def check_metadata():
    """Check Metadata."""
    import importlib.metadata as md
    print("[OK] Version:", md.version("saab_suite"))

if __name__ == "__main__":
    check_imports()
    check_plugins()
    check_cli()
    check_runtime()
    check_metadata()
