import threading
import time
from typing import Dict, Any
from .board import IncidentBoard

class LogsAgent(threading.Thread):
    """Simulates fetching recent logs for the affected service and posts them.
    It waits for an ``alert`` entry, then creates a ``logs`` entry.
    """
    def __init__(self, board: IncidentBoard):
        super().__init__(daemon=True)
        self.board = board
        self.processed_alerts = set()

    def run(self):
        while True:
            alerts = self.board.query("alert")
            for alert in alerts:
                alert_id = alert.get("timestamp")
                if alert_id in self.processed_alerts:
                    continue
                # Simulate log retrieval (placeholder data)
                service = alert["data"].get("service", "unknown")
                logs = [
                    f"{service} - ERROR - Something failed at {time.time() - 30}s",
                    f"{service} - INFO - Restart attempted",
                ]
                entry = {
                    "type": "logs",
                    "timestamp": time.time(),
                    "data": {"service": service, "logs": logs},
                    "ref": alert_id,
                }
                self.board.post(entry)
                print("[LogsAgent] Posted logs for", service)
                self.processed_alerts.add(alert_id)
            time.sleep(1)
