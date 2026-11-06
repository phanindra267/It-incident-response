import time
from src.board import IncidentBoard
from src.alert_agent import AlertAgent
from src.logs_agent import LogsAgent
from src.dependency_agent import DependencyAgent
from src.mitigation_agent import MitigationAgent
from src.commander_agent import CommanderAgent
from src.comms_agent import CommsAgent

def main():
    board = IncidentBoard()
    # Start background agents (except AlertAgent which will be instantiated per alert)
    agents = [
        LogsAgent(board),
        DependencyAgent(board),
        MitigationAgent(board),
        CommanderAgent(board),
        CommsAgent(board),
    ]
    for agent in agents:
        agent.start()
    print("[Demo] Background agents started.")

    # Post an alert
    alert_payload = {"service": "service-a", "symptom": "high latency", "severity": "high"}
    alert_agent = AlertAgent(board, alert=alert_payload)
    alert_agent.start()
    print("[Demo] Alert posted:", alert_payload)

    # Wait for the workflow to complete
    time.sleep(5)

    # Display board entries
    print("\n=== Incident Board ===")
    for entry in board.get_all():
        ts = time.ctime(entry["timestamp"]) if isinstance(entry["timestamp"], (int, float)) else entry["timestamp"]
        print(f"{ts} | {entry.get('type')} | {entry.get('data')}")

if __name__ == "__main__":
    main()
