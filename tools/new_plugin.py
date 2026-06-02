#!/usr/bin/env python3
from pathlib import Path
import sys, textwrap

ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = ROOT / "plugins"

def main(name: str):
    pkg_name = f"saab-suite-{name}"
    mod_name = f"saab_suite_{name}"
    base = PLUGINS_DIR / pkg_name
    src_dir = base / "src" / mod_name
    src_dir.mkdir(parents=True, exist_ok=True)

    (src_dir / "__init__.py").write_text("")
    (src_dir / "plugin.py").write_text(
        textwrap.dedent(
            f"""
            from SAAB-SUITE.plugins.base import BasePlugin

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
            dependencies = ["SAAB-SUITE"]

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
