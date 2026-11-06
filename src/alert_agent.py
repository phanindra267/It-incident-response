import threading
import time
from typing import Dict, Any
from .board import IncidentBoard

class AlertAgent(threading.Thread):
    """Posts an incident alert to the board.
    In a real system this would listen to monitoring tools; here we simulate.
    """
    def __init__(self, board: IncidentBoard, alert: Dict[str, Any]):
        super().__init__(daemon=True)
        self.board = board
        self.alert = alert

    def run(self):
        entry = {
            "type": "alert",
            "timestamp": time.time(),
            "data": self.alert,
        }
        self.board.post(entry)
        print("[AlertAgent] Posted alert:", self.alert)
