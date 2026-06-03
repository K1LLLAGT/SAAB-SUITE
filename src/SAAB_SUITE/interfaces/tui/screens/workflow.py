from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem
from textual.screen import Screen
from pathlib import Path
import json

WORKFLOWS_DIR = Path(__file__).resolve().parents[4] / "runtime" / "workflows"

class WorkflowScreen(Screen):
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Workflows", id="title")
        yield ListView(*self._workflow_items(), id="workflow-list")
        yield Footer()

    def _workflow_items(self):
        items = []
        for path in sorted(WORKFLOWS_DIR.glob("*.json")):
            data = json.loads(path.read_text())
            label = data.get("name", path.stem)
            items.append(ListItem(Static(label), id=path.stem))
        return items
