#!/usr/bin/env python3
from importlib import import_module
import subprocess
import pkg_resources

def check_imports():
    modules = [
        "SAAB-SUITE",
        "SAAB-SUITE.interfaces.cli.main",
        "SAAB-SUITE.services.vin.decoder",
        "SAAB-SUITE.services.sps.plan_builder",
    ]
    for m in modules:
        import_module(m)
    print("[OK] Core imports")

def check_plugins():
    eps = list(pkg_resources.iter_entry_points("saab_suite.plugins"))
    print(f"[OK] {len(eps)} plugins detected")
    for ep in eps:
        ep.load()

def check_cli():
    subprocess.run(["saab-suite", "--help"], check=True, capture_output=True)
    subprocess.run(["saab-suite", "diag", "--help"], check=True, capture_output=True)
    print("[OK] CLI entrypoints")

def check_runtime():
    from SAAB-SUITE.runtime import paths
    for p in [paths.LOG_DIR, paths.CACHE_DIR, paths.BACKUP_DIR, paths.LOCK_DIR]:
        print("[OK] Runtime path:", p)
    paths.ensure_dirs()

def check_metadata():
    import importlib.metadata as md
    print("[OK] Version:", md.version("SAAB-SUITE"))

if __name__ == "__main__":
    check_imports()
    check_plugins()
    check_cli()
    check_runtime()
    check_metadata()
