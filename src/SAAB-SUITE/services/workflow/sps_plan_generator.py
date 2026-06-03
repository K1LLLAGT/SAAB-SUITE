from pathlib import Path
import json
from typing import List, Dict, Any

from SAAB-SUITE.services.sps.plan_builder import PlanBuilder

WORKFLOWS_DIR = Path(__file__).resolve().parents[3] / "runtime" / "workflows"

def load_workflow(name: str) -> Dict[str, Any]:
    path = WORKFLOWS_DIR / f"{name}.json"
    data = json.loads(path.read_text())
    return data

def build_sps_plan_from_workflow(name: str):
    wf = load_workflow(name)
    steps = wf.get("steps", [])
    builder = PlanBuilder()

    for step in steps:
        if step.get("type") == "sps":
            module = step["module"]
            deliverable = step.get("deliverable")
            builder.add_flash_step(module=module, deliverable=deliverable)

    return builder.build()
