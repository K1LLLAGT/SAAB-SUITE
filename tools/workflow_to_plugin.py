#!/usr/bin/env python3
import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = ROOT / "plugins"
WORKFLOWS_DIR = ROOT / "runtime" / "workflows"

def main(workflow_name: str):
    """Run the command-line entry point."""
    wf_file = WORKFLOWS_DIR / f"{workflow_name}.json"
    if not wf_file.exists():
        print(f"Workflow definition not found: {wf_file}")
        sys.exit(1)

    data = json.loads(wf_file.read_text())
    desc = data.get("description", f"Workflow {workflow_name}")

    pkg_name = f"saab-workflow-{workflow_name}"
    mod_name = f"saab_suite_workflow_{workflow_name}"
    base = PLUGINS_DIR / pkg_name
    src_dir = base / "src" / mod_name
    src_dir.mkdir(parents=True, exist_ok=True)

    (src_dir / "__init__.py").write_text("")
    (src_dir / "plugin.py").write_text(
        textwrap.dedent(
            f"""
            from saab_suite.plugins.base import BasePlugin
            from saab_suite.services.workflow.engine import run_workflow

            class Plugin(BasePlugin):
                name = "workflow-{workflow_name}"
                description = {desc!r}

                def register(self, registry):
                    registry.register_workflow("{workflow_name}", run_workflow)
            """
        ).lstrip()
    )

    (base / "pyproject.toml").write_text(
        textwrap.dedent(
            f"""
            [project]
            name = "{pkg_name}"
            version = "0.1.0"
            dependencies = ["saab_suite"]

            [project.entry-points."saab_suite.plugins"]
            workflow_{workflow_name} = "{mod_name}.plugin:Plugin"
            """
        ).lstrip()
    )

    print(f"Created workflow plugin at {base}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: tools/workflow_to_plugin.py <workflow_name>")
        sys.exit(1)
    main(sys.argv[1])
