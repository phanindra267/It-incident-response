import threading
import time
from typing import Dict, Any
from .board import IncidentBoard

class MitigationAgent(threading.Thread):
    """Proposes a mitigation based on alert, logs, and dependencies.
    Waits until all three required entries are present for a given alert.
    """
    def __init__(self, board: IncidentBoard):
        super().__init__(daemon=True)
        self.board = board
        self.processed_alerts = set()

    def _has_all_evidence(self, alert_id: float) -> bool:
        required = {"logs", "dependency"}
        present = {e["type"] for e in self.board.entries if e.get("ref") == alert_id}
        return required.issubset(present)

    def _decide_mitigation(self, alert: Dict[str, Any], logs: Dict[str, Any], deps: Dict[str, Any]) -> str:
        # Simple rule‑based placeholder logic
        severity = alert["data"].get("severity", "low").lower()
        if severity == "high":
            return "rollback"
        elif logs["data"]["logs"] and any("ERROR" in line for line in logs["data"]["logs"]):
            return "restart"
        else:
            return "failover"

    def run(self):
        while True:
            alerts = self.board.query("alert")
            for alert in alerts:
                alert_id = alert.get("timestamp")
                if alert_id in self.processed_alerts:
                    continue
                if not self._has_all_evidence(alert_id):
                    continue  # wait for logs & dependencies
                # Retrieve related entries
                logs_entry = next(e for e in self.board.entries if e.get("type") == "logs" and e.get("ref") == alert_id)
                dep_entry = next(e for e in self.board.entries if e.get("type") == "dependency" and e.get("ref") == alert_id)
                mitigation = self._decide_mitigation(alert, logs_entry, dep_entry)
                entry = {
                    "type": "mitigation",
                    "timestamp": time.time(),
                    "data": {
                        "service": alert["data"].get("service"),
                        "action": mitigation,
                    },
                    "ref": alert_id,
                }
                self.board.post(entry)
                print(f"[MitigationAgent] Proposed mitigation '{mitigation}' for", alert["data"].get("service"))
                self.processed_alerts.add(alert_id)
            time.sleep(1)
