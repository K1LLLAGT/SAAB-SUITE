#!/usr/bin/env bash
set -euo pipefail

echo "=============================================="
echo "   SAAB-SUITE + WORKFLOW SUPER-MERGE SCRIPT"
echo "=============================================="

# CONFIG
SUITE_REPO="https://github.com/K1LLLAGT/SAAB-SUITE.git"
WORKFLOW_REPO="https://github.com/K1LLLAGT/saab-diagnostic-workflow.git"
MERGE_DIR="$HOME/saab_merge_temp"

echo "[*] Creating temp merge directory..."
rm -rf "$MERGE_DIR"
mkdir -p "$MERGE_DIR"
cd "$MERGE_DIR"

echo "[*] Cloning SAAB-SUITE..."
git clone "$SUITE_REPO" SAAB-SUITE
cd SAAB-SUITE

echo "[*] Adding workflow repo as remote..."
git remote add workflow "$WORKFLOW_REPO"
git fetch workflow

echo "[*] Subtree merging workflow repo..."
git subtree add --prefix=workflow workflow main --squash

echo "[*] Moving workflow docs into docs/workflows..."
mkdir -p docs/workflows
if [ -d workflow/docs ]; then
    mv workflow/docs/* docs/workflows/
fi

echo "[*] Moving workflow code into services/workflow..."
mkdir -p src/SAAB-SUITE/services/workflow
if [ -d workflow/src ]; then
    mv workflow/src/* src/SAAB-SUITE/services/workflow/
fi

echo "[*] Moving workflow assets into runtime/workflows..."
mkdir -p runtime/workflows
if [ -d workflow/assets ]; then
    mv workflow/assets/* runtime/workflows/
fi

echo "[*] Removing temporary workflow directory..."
rm -rf workflow

echo "[*] Updating imports from 'saab_diagnostic_workflow' to 'SAAB-SUITE.services.workflow'..."
grep -rl "saab_diagnostic_workflow" src/SAAB-SUITE/services/workflow | while read -r file; do
    sed -i 's/saab_diagnostic_workflow/SAAB-SUITE.services.workflow/g' "$file"
done

echo "[*] Updating CLI to include workflow commands..."
CLI_FILE="src/SAAB-SUITE/interfaces/cli/main.py"
if ! grep -q "workflow" "$CLI_FILE"; then
    cat >> "$CLI_FILE" << 'EOC'

# Workflow CLI integration
from SAAB-SUITE.services.workflow import cli as workflow_cmd
app.add_typer(workflow_cmd.app, name="workflow")
EOC
fi

echo "[*] Updating pyproject.toml to include workflow package..."
if ! grep -q "SAAB-SUITE.services.workflow" pyproject.toml; then
    sed -i '/packages = \[/a\    "SAAB-SUITE.services.workflow",' pyproject.toml
fi

echo "[*] Updating documentation index..."
cat >> docs/README.md << 'EOD'

## Workflow Documentation
See docs/workflows/ for SPS flows, VIN logic, and diagnostic sequences.
EOD

echo "[*] Running cleanup..."
tools/cleanup.sh || true

echo "[*] Running audit..."
tools/audit_imports.py || true

echo "[*] Running integrity checks..."
tools/post_migration_check.py || true

echo "[*] Staging merge changes..."
git add -A

if git diff --cached --quiet; then
    echo "No changes to commit."
else
    echo "[*] Committing merge..."
    git commit -m "Merge saab-diagnostic-workflow into SAAB-SUITE (automated super-merge)"

    echo "[*] Pushing to GitHub..."
    git push
fi

echo "=============================================="
echo " SUPER-MERGE COMPLETE — WORKFLOW IS NOW PART OF SAAB-SUITE"
echo "=============================================="
