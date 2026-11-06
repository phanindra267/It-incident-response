import threading
import time
from typing import Dict, Any
from .board import IncidentBoard

class CommanderAgent(threading.Thread):
    """Reads the board, decides on final action, and records a timeline.
    It waits for a ``mitigation`` entry, then creates a ``decision`` entry and
    appends a human‑readable ``timeline`` entry that summarises the incident.
    """
    def __init__(self, board: IncidentBoard):
        super().__init__(daemon=True)
        self.board = board
        self.processed_alerts = set()

    def _build_timeline(self, alert: Dict[str, Any], logs: Dict[str, Any], dep: Dict[str, Any], mitigation: Dict[str, Any]) -> str:
        lines = []
        lines.append(f"### Incident Timeline for {alert['data'].get('service', 'unknown')}\n")
        lines.append(f"* **Alert** (severity: {alert['data'].get('severity', 'n/a')}) posted at {time.ctime(alert['timestamp'])}\n")
        lines.append(f"* **Logs** collected at {time.ctime(logs['timestamp'])}:\n")
        for line in logs['data']['logs']:
            lines.append(f"    - {line}\n")
        lines.append(f"* **Dependencies** identified at {time.ctime(dep['timestamp'])}: {', '.join(dep['data'].get('upstream', [])) or 'none'}\n")
        lines.append(f"* **Mitigation** proposed at {time.ctime(mitigation['timestamp'])}: **{mitigation['data']['action']}**\n")
        lines.append(f"* **Decision** recorded at {time.ctime(time.time())}: proceed with **{mitigation['data']['action']}**\n")
        return "".join(lines)

    def run(self):
        while True:
            alerts = self.board.query("alert")
            for alert in alerts:
                alert_id = alert.get("timestamp")
                if alert_id in self.processed_alerts:
                    continue
                # Ensure mitigation exists
                mitigation_entries = [e for e in self.board.entries if e.get("type") == "mitigation" and e.get("ref") == alert_id]
                if not mitigation_entries:
                    continue  # wait for mitigation
                mitigation = mitigation_entries[0]
                # Retrieve related evidence for timeline
                logs = next(e for e in self.board.entries if e.get("type") == "logs" and e.get("ref") == alert_id)
                dep = next(e for e in self.board.entries if e.get("type") == "dependency" and e.get("ref") == alert_id)
                # Record decision
                decision_entry = {
                    "type": "decision",
                    "timestamp": time.time(),
                    "data": {
                        "service": alert["data"].get("service"),
                        "action": mitigation["data"]["action"],
                    },
                    "ref": alert_id,
                }
                self.board.post(decision_entry)
                # Record timeline as a markdown string
                timeline_md = self._build_timeline(alert, logs, dep, mitigation)
                timeline_entry = {
                    "type": "timeline",
                    "timestamp": time.time(),
                    "data": {"markdown": timeline_md},
                    "ref": alert_id,
                }
                self.board.post(timeline_entry)
                print(f"[CommanderAgent] Decision recorded and timeline generated for {alert['data'].get('service')}")
                self.processed_alerts.add(alert_id)
            time.sleep(1)
