import json
from pathlib import Path
from typing import Any

from saab_suite.services.sps.plan_builder import PlanBuilder

WORKFLOWS_DIR = Path(__file__).resolve().parents[3] / "runtime" / "workflows"

def load_workflow(name: str) -> dict[str, Any]:
    """Load workflow."""
    path = WORKFLOWS_DIR / f"{name}.json"
    data = json.loads(path.read_text())
    return data

def build_sps_plan_from_workflow(name: str):
    """Build the sps plan from workflow."""
    wf = load_workflow(name)
    steps = wf.get("steps", [])
    builder = PlanBuilder()

    for step in steps:
        if step.get("type") == "sps":
            module = step["module"]
            deliverable = step.get("deliverable")
            builder.add_flash_step(module=module, deliverable=deliverable)

    return builder.build()
