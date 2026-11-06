import threading
from typing import List, Dict, Any

class IncidentBoard:
    """Thread‑safe blackboard for incident information.
    Agents post dict entries with a ``type`` field indicating the kind of
    information (e.g. ``alert``, ``logs``, ``dependency``, ``mitigation``,
    ``decision``). The board holds a chronological list of posts.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self.entries: List[Dict[str, Any]] = []

    def post(self, entry: Dict[str, Any]):
        """Add a new entry to the board.
        ``entry`` must contain at least a ``type`` and a ``timestamp``.
        """
        with self._lock:
            self.entries.append(entry)

    def get_all(self) -> List[Dict[str, Any]]:
        """Return a copy of all entries ordered by insertion time."""
        with self._lock:
            return list(self.entries)

    def query(self, entry_type: str) -> List[Dict[str, Any]]:
        """Return entries of a specific ``type``."""
        with self._lock:
            return [e for e in self.entries if e.get("type") == entry_type]
