import threading
import time
from typing import Dict, Any
from .board import IncidentBoard

class DependencyAgent(threading.Thread):
    """Analyzes service dependencies after an alert and posts them.
    For demonstration, it uses a static mapping.
    """
    _dependency_map = {
        "service-a": ["service-b", "service-c"],
        "service-b": ["service-d"],
        "service-c": [],
    }

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
                service = alert["data"].get("service", "unknown")
                deps = self._dependency_map.get(service, [])
                entry = {
                    "type": "dependency",
                    "timestamp": time.time(),
                    "data": {"service": service, "upstream": deps},
                    "ref": alert_id,
                }
                self.board.post(entry)
                print("[DependencyAgent] Posted dependencies for", service)
                self.processed_alerts.add(alert_id)
            time.sleep(1)
