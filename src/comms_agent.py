import threading
import time
from typing import Dict, Any
from .board import IncidentBoard

class CommsAgent(threading.Thread):
    """Generates a status‑page update based on the latest decision.
    For each severity level it drafts a markdown snippet and posts it as a
    ``status`` entry on the board.
    """
    def __init__(self, board: IncidentBoard):
        super().__init__(daemon=True)
        self.board = board
        self.processed_decisions = set()

    def _draft_update(self, decision: Dict[str, Any], alert: Dict[str, Any]) -> str:
        severity = alert["data"].get("severity", "low").lower()
        service = alert["data"].get("service", "unknown")
        action = decision["data"].get("action", "unknown")
        markdown = f"## Incident Update - {service}\n"
        markdown += f"**Severity:** {severity}\n\n"
        markdown += f"The incident was diagnosed and the following mitigation was applied: **{action}**."
        return markdown

    def run(self):
        while True:
            decisions = [e for e in self.board.entries if e.get("type") == "decision"]
            for decision in decisions:
                decision_id = decision.get("timestamp")
                if decision_id in self.processed_decisions:
                    continue
                # Find the original alert this decision references
                alert = next(
                    (a for a in self.board.entries if a.get("type") == "alert" and a.get("timestamp") == decision.get("ref")),
                    None,
                )
                if not alert:
                    continue
                status_md = self._draft_update(decision, alert)
                entry = {
                    "type": "status",
                    "timestamp": time.time(),
                    "data": {"markdown": status_md},
                    "ref": decision_id,
                }
                self.board.post(entry)
                print(f"[CommsAgent] Posted status update for {alert['data'].get('service')}")
                self.processed_decisions.add(decision_id)
            time.sleep(1)
