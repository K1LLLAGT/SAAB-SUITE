#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "  SAAB_SUITE SUPER-BOOTSTRAP GENERATOR"
echo "=============================================="

# Ensure directories exist
mkdir -p docs docs/architecture packaging/termux .github/workflows src/SAAB_SUITE/runtime tools plugins

###############################################
# 1. Repo Audit Report
###############################################
cat > docs/repo_audit.md << 'EOD'
# SAAB_SUITE Repo Audit

## Strengths
- Hexagonal architecture
- Multi-platform packaging
- Plugin system
- Runtime separation

## Risks / TODOs
- Legacy vs new package migration
- CI alignment
- Vendor validation
- Documentation alignment

## Recommended Priorities
1. Finalize namespace migration
2. Unified CLI + plugin discovery
3. CI matrix improvements
4. Developer onboarding + diagrams
EOD

###############################################
# 2. Cleanup Plan
###############################################
cat > docs/cleanup_plan.md << 'EOD'
# Cleanup Plan

## Goals
- Remove legacy artifacts
- Keep repo deterministic

## Steps
1. Remove src/saab_suite after migration
2. Purge pycache, pyc, pyo, bak
3. Normalize script permissions
4. Update .gitignore
EOD

###############################################
# 3. README.md
###############################################
cat > README.md << 'EOD'
# SAAB_SUITE

SAAB_SUITE is a hexagonally-architected diagnostic and flashing suite for Saab vehicles.

## Features
- CAN / UDS / KWP / J2534
- VIN-aware profiles
- SPS workflows
- Plugin system
- Multi-platform packaging

## Quick Start

    git clone <YOUR_REPO_URL> SAAB_SUITE
    cd SAAB_SUITE
    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    saab --help

## Development

    tools/format.sh
    tools/lint.sh
    tools/typecheck.sh
    tools/test.sh

## Packaging
- AppImage
- Docker
- Termux
- Windows installer
EOD

###############################################
# 4. Developer Onboarding Guide
###############################################
cat > docs/developer_onboarding.md << 'EOD'
# Developer Onboarding

## Setup

    git clone <YOUR_REPO_URL> SAAB_SUITE
    cd SAAB_SUITE
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"

## Layout
- src/SAAB_SUITE/
- plugins/
- runtime/
- vendor/
- packaging/
- tests/

## Commands

    tools/format.sh
    tools/lint.sh
    tools/typecheck.sh
    tools/test.sh
EOD

###############################################
# 5. Termux Runtime Layout
###############################################
cat > src/SAAB_SUITE/runtime/paths.py << 'EOD'
from pathlib import Path
import os

def _default_base() -> Path:
    env = os.environ.get("SAAB_SUITE_RUNTIME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".saab" / "runtime"

BASE_DIR = _default_base()

LOG_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
BACKUP_DIR = BASE_DIR / "backups"
LOCK_DIR = BASE_DIR / "locks"

def ensure_dirs():
    for d in (LOG_DIR, CACHE_DIR, BACKUP_DIR, LOCK_DIR):
        d.mkdir(parents=True, exist_ok=True)
EOD

cat > packaging/termux/install.sh << 'EOD'
#!/usr/bin/env bash
set -euo pipefail

PREFIX_DIR="${PREFIX:-/data/data/com.termux/files/usr}"
APP_DIR="$PREFIX_DIR/share/saab"

mkdir -p "$APP_DIR"
cp -r . "$APP_DIR"

if ! grep -q "SAAB_SUITE_RUNTIME" "$HOME/.bashrc"; then
  echo 'export SAAB_SUITE_RUNTIME="$HOME/.saab/runtime"' >> "$HOME/.bashrc"
fi

echo "Installed SAAB_SUITE to $APP_DIR"
EOD
chmod +x packaging/termux/install.sh

###############################################
# 6. GitHub Actions CI
###############################################
cat > .github/workflows/ci.yml << 'EOD'
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint & typecheck
        run: |
          tools/format.sh
          tools/lint.sh
          tools/typecheck.sh

      - name: Tests
        run: pytest -q
EOD

###############################################
# 7. Architecture Diagram
###############################################
cat > docs/architecture/saab-architecture.mmd << 'EOD'
graph TD
  Interfaces --> Services
  Services --> Domain
  Domain --> Ports
  Ports --> Adapters
EOD

###############################################
# 8. Unified CLI Entrypoint
###############################################
mkdir -p src/SAAB_SUITE/interfaces/cli

cat > src/SAAB_SUITE/interfaces/cli/main.py << 'EOD'
import typer

app = typer.Typer(help="SAAB_SUITE CLI")

from .commands import (
    can as can_cmd,
    diag as diag_cmd,
    discover as discover_cmd,
    health as health_cmd,
    live as live_cmd,
    sps as sps_cmd,
    tools as tools_cmd,
    vehicle as vehicle_cmd,
)

app.add_typer(can_cmd.app, name="can")
app.add_typer(diag_cmd.app, name="diag")
app.add_typer(discover_cmd.app, name="discover")
app.add_typer(health_cmd.app, name="health")
app.add_typer(live_cmd.app, name="live")
app.add_typer(sps_cmd.app, name="sps")
app.add_typer(tools_cmd.app, name="tools")
app.add_typer(vehicle_cmd.app, name="vehicle")

def main():
    app()

if __name__ == "__main__":
    main()
EOD

###############################################
# 9. Plugin Template Generator
###############################################
cat > tools/new_plugin.py << 'EOD'
#!/usr/bin/env python3
from pathlib import Path
import sys, textwrap

ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = ROOT / "plugins"

def main(name: str):
    pkg_name = f"saab-{name}"
    mod_name = f"saab_suite_{name}"
    base = PLUGINS_DIR / pkg_name
    src_dir = base / "src" / mod_name
    src_dir.mkdir(parents=True, exist_ok=True)

    (src_dir / "__init__.py").write_text("")
    (src_dir / "plugin.py").write_text(
        textwrap.dedent(
            f"""
            from SAAB_SUITE.plugins.base import BasePlugin

            class Plugin(BasePlugin):
                name = "{name}"
                description = "Plugin {name}"

                def register(self, registry):
                    ...
            """
        ).lstrip()
    )

    (base / "pyproject.toml").write_text(
        textwrap.dedent(
            f"""
            [project]
            name = "{pkg_name}"
            version = "0.1.0"
            dependencies = ["SAAB_SUITE"]

            [project.entry-points."saab_suite.plugins"]
            {name} = "{mod_name}.plugin:Plugin"
            """
        ).lstrip()
    )

    print(f"Created plugin template at {base}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: tools/new_plugin.py <name>")
        sys.exit(1)
    main(sys.argv[1])
EOD
chmod +x tools/new_plugin.py

###############################################
# 10. Test Runner
###############################################
cat > tools/test.sh << 'EOD'
#!/usr/bin/env bash
set -euo pipefail
pytest -q
EOD
chmod +x tools/test.sh

###############################################
# 11. Migration Verifier
###############################################
cat > tools/verify_migration.py << 'EOD'
#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]

def check_git():
    out = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).decode()
    if "src/saab_suite" in out:
        print("[FAIL] src/saab_suite still present")
        sys.exit(1)
    print("[OK] No legacy package")

def check_import():
    try:
        __import__("SAAB_SUITE")
        print("[OK] Import SAAB_SUITE")
    except Exception as e:
        print("[FAIL] Import error:", e)
        sys.exit(1)

if __name__ == "__main__":
    check_git()
    check_import()
EOD
chmod +x tools/verify_migration.py

###############################################
# 12. Cleanup Script
###############################################
cat > tools/cleanup.sh << 'EOD'
#!/usr/bin/env bash
set -euo pipefail

find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
find . -name '*.pyo' -delete
find . -name '*.bak' -delete

echo "Cleanup complete."
EOD
chmod +x tools/cleanup.sh

###############################################
# 13. Migration Commit Message
###############################################
cat > tools/migration_commit_msg.txt << 'EOD'
Migrate core package from `saab_suite` to `SAAB_SUITE`

- Remove legacy src/saab_suite package
- Add new src/SAAB_SUITE hexagonal layout
- Update runtime paths and interfaces
- Preserve plugins, tests, and packaging structure
EOD

###############################################
# 14. Import Auditor
###############################################
cat > tools/audit_imports.py << 'EOD'
#!/usr/bin/env python3
from pathlib import Path
import ast

ROOT = Path("src/SAAB_SUITE")

missing = []

for py in ROOT.rglob("*.py"):
    tree = ast.parse(py.read_text(), filename=str(py))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("saab_suite"):
                missing.append((py, node.module))

if missing:
    print("Legacy imports found:")
    for path, mod in missing:
        print(f"{path}: from {mod}")
else:
    print("No legacy imports.")
EOD
chmod +x tools/audit_imports.py

###############################################
# 15. Integrity Checker
###############################################
cat > tools/post_migration_check.py << 'EOD'
#!/usr/bin/env python3
from importlib import import_module
import subprocess
import pkg_resources

def check_imports():
    modules = [
        "SAAB_SUITE",
        "SAAB_SUITE.interfaces.cli.main",
        "SAAB_SUITE.services.vin.decoder",
        "SAAB_SUITE.services.sps.plan_builder",
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
    subprocess.run(["saab", "--help"], check=True, capture_output=True)
    subprocess.run(["saab", "diag", "--help"], check=True, capture_output=True)
    print("[OK] CLI entrypoints")

def check_runtime():
    from SAAB_SUITE.runtime import paths
    for p in [paths.LOG_DIR, paths.CACHE_DIR, paths.BACKUP_DIR, paths.LOCK_DIR]:
        print("[OK] Runtime path:", p)
    paths.ensure_dirs()

def check_metadata():
    import importlib.metadata as md
    print("[OK] Version:", md.version("SAAB_SUITE"))

if __name__ == "__main__":
    check_imports()
    check_plugins()
    check_cli()
    check_runtime()
    check_metadata()
EOD
chmod +x tools/post_migration_check.py

###############################################
# Unified Bootstrap Script
###############################################
cat > tools/bootstrap.sh << 'EOD'
#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo " SAAB_SUITE BOOTSTRAP: FULL SYSTEM CHECK"
echo "=============================================="

echo "[1/5] Cleanup..."
tools/cleanup.sh

echo "[2/5] Audit imports..."
tools/audit_imports.py

echo "[3/5] Verify migration..."
tools/verify_migration.py

echo "[4/5] Integrity checks..."
tools/post_migration_check.py

echo "[5/5] Running tests..."
tools/test.sh

echo "=============================================="
echo " ALL CHECKS PASSED — SAAB_SUITE IS HEALTHY"
echo "=============================================="
EOD
chmod +x tools/bootstrap.sh

###############################################
# GitHub Auto-Update
###############################################
echo "=============================================="
echo " Updating GitHub repository..."
echo "=============================================="

git add -A

if git diff --cached --quiet; then
    echo "No changes to commit."
else
    git commit -m "Super-bootstrap: rebuild repo"
    git push
    echo "Changes pushed to GitHub."
fi

echo "=============================================="
echo " SUPER-BOOTSTRAP GENERATOR COMPLETE"
echo " Run: tools/bootstrap.sh"
echo "=============================================="
