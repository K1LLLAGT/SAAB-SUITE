from fastapi import APIRouter
from pathlib import Path
import json

from SAAB-SUITE.services.workflow.engine import run_workflow

router = APIRouter(prefix="/workflow", tags=["workflow"])

WORKFLOWS_DIR = Path(__file__).resolve().parents[4] / "runtime" / "workflows"

@router.get("/")
def list_workflows():
    items = []
    for path in sorted(WORKFLOWS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        items.append({"id": path.stem, "name": data.get("name", path.stem)})
    return items

@router.post("/{workflow_id}/run")
def run(workflow_id: str, vin: str):
    result = run_workflow(workflow_id, vin=vin)
    return {"workflow": workflow_id, "vin": vin, "result": result}
