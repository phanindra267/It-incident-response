import time
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from .board import IncidentBoard
from .alert_agent import AlertAgent
from .logs_agent import LogsAgent
from .dependency_agent import DependencyAgent
from .mitigation_agent import MitigationAgent
from .commander_agent import CommanderAgent
from .comms_agent import CommsAgent

app = FastAPI(title="Incident Response War‑Room")

# Shared blackboard instance
board = IncidentBoard()

# Agent instances (daemon threads) – started on startup event
agents: List[threading.Thread] = [
    AlertAgent(board, alert={}),  # placeholder, will be used per request
    LogsAgent(board),
    DependencyAgent(board),
    MitigationAgent(board),
    CommanderAgent(board),
    CommsAgent(board),
]

@app.on_event("startup")
async def start_agents():
    # Start all agents except AlertAgent which will be instantiated per alert request
    for agent in agents[1:]:
        agent.start()
    print("[Main] All background agents started.")

class AlertPayload(BaseModel):
    service: str = Field(..., description="Name of the affected service")
    symptom: str = Field(..., description="Brief description of the symptom")
    severity: str = Field(..., description="Severity level (low, medium, high)")

@app.post("/alert")
async def post_alert(payload: AlertPayload):
    # Create a dedicated AlertAgent for this incident and run it once
    alert_data = payload.dict()
    agent = AlertAgent(board, alert=alert_data)
    agent.start()
    # Give a tiny moment for the alert to be posted
    time.sleep(0.1)
    return {"status": "alert posted", "payload": alert_data}

@app.get("/board")
async def get_board():
    # Return a copy of the board entries sorted by timestamp
    entries = board.get_all()
    # Convert timestamps to readable strings for API consumers
    for e in entries:
        e["timestamp"] = time.ctime(e["timestamp"]) if isinstance(e["timestamp"], (int, float)) else e["timestamp"]
    return {"entries": entries}

@app.get("/interactive", response_class=HTMLResponse)
async def interactive_simulator():
    with open("interactive_simulator.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def war_room_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>IT Incident Response War-Room</title>
    <style>
        :root {
            --bg: #0d1117; --card-bg: #161b22; --border: #30363d;
            --text: #c9d1d9; --accent: #58a6ff; --red: #f85149;
            --yellow: #e3b341; --green: #3fb950; --purple: #bc8cff;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            background: var(--bg); color: var(--text); margin: 0; padding: 20px;
        }
        .header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--border); padding-bottom: 15px; margin-bottom: 20px;
        }
        .header h1 { margin: 0; font-size: 24px; color: #fff; }
        .badge {
            background: #238636; color: white; padding: 4px 10px;
            border-radius: 12px; font-size: 12px; font-weight: bold;
        }
        .grid { display: grid; grid-template-columns: 340px 1fr; gap: 20px; }
        .card {
            background: var(--card-bg); border: 1px solid var(--border);
            border-radius: 8px; padding: 18px;
        }
        .card h2 { margin-top: 0; font-size: 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
        label { display: block; font-size: 13px; margin: 10px 0 4px; color: #8b949e; }
        input, select {
            width: 100%; box-sizing: border-box; background: #0d1117;
            border: 1px solid var(--border); color: #fff; padding: 8px;
            border-radius: 6px; font-size: 13px;
        }
        button {
            margin-top: 15px; width: 100%; background: #238636; color: white;
            border: none; padding: 10px; border-radius: 6px; font-weight: bold;
            cursor: pointer; transition: 0.2s;
        }
        button:hover { background: #2ea043; }
        .board-entry {
            background: #0d1117; border-left: 4px solid var(--accent);
            padding: 12px; margin-bottom: 12px; border-radius: 4px;
            border-top: 1px solid var(--border); border-right: 1px solid var(--border); border-bottom: 1px solid var(--border);
        }
        .entry-alert { border-left-color: var(--red); }
        .entry-logs { border-left-color: var(--yellow); }
        .entry-dependency { border-left-color: var(--purple); }
        .entry-mitigation { border-left-color: #388bfd; }
        .entry-decision { border-left-color: var(--green); }
        .entry-timeline { border-left-color: #f0883e; }
        .entry-status { border-left-color: #a371f7; }
        .entry-meta { display: flex; justify-content: space-between; font-size: 12px; color: #8b949e; margin-bottom: 6px; }
        .entry-type { font-weight: bold; text-transform: uppercase; }
        pre { margin: 0; font-size: 12px; white-space: pre-wrap; font-family: inherit; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 IT Incident Response War-Room</h1>
        <div style="display:flex; align-items:center; gap:10px;">
            <a href="/interactive" target="_blank" style="background:#0284c7; color:#fff; text-decoration:none; padding:6px 14px; border-radius:6px; font-size:12px; font-weight:bold;">🎬 Launch Animated Simulator</a>
            <div class="badge">● Multi-Agent Blackboard Active</div>
        </div>
    </div>
    <div class="grid">
        <div class="card">
            <h2>Post Incident Signal</h2>
            <form id="alertForm">
                <label>Affected Service</label>
                <input type="text" id="service" value="payment-gateway" required>

                <label>Symptom</label>
                <input type="text" id="symptom" value="504 Gateway Timeout during checkout" required>

                <label>Severity Level</label>
                <select id="severity">
                    <option value="high" selected>High (Sev-1)</option>
                    <option value="medium">Medium (Sev-2)</option>
                    <option value="low">Low (Sev-3)</option>
                </select>

                <button type="submit">🚨 Trigger Incident Alert</button>
            </form>
            <div style="margin-top: 20px; font-size: 12px; color: #8b949e; line-height: 1.5;">
                <strong>War-Room Agents:</strong><br>
                • <b>Alert Agent:</b> Signals incident<br>
                • <b>Logs Agent:</b> Fetches telemetry<br>
                • <b>Dependency Agent:</b> Analyzes map<br>
                • <b>Mitigation Agent:</b> Proposes fix<br>
                • <b>Commander Agent:</b> Decides & builds timeline<br>
                • <b>Comms Agent:</b> Drafts status update
            </div>
        </div>
        <div class="card">
            <h2>Live Incident Board (Blackboard Memory)</h2>
            <div id="boardFeed">Waiting for updates...</div>
        </div>
    </div>

    <script>
        document.getElementById('alertForm').onsubmit = async (e) => {
            e.preventDefault();
            const payload = {
                service: document.getElementById('service').value,
                symptom: document.getElementById('symptom').value,
                severity: document.getElementById('severity').value
            };
            await fetch('/alert', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            fetchBoard();
        };

        async function fetchBoard() {
            try {
                const res = await fetch('/board');
                const data = await res.json();
                const feed = document.getElementById('boardFeed');
                if (!data.entries || data.entries.length === 0) {
                    feed.innerHTML = '<p style="color:#8b949e;">No active incident entries on the board.</p>';
                    return;
                }
                feed.innerHTML = data.entries.slice().reverse().map(e => {
                    const typeClass = 'entry-' + (e.type || 'default');
                    let content = '';
                    if (e.data && e.data.markdown) {
                        content = e.data.markdown;
                    } else {
                        content = JSON.stringify(e.data, null, 2);
                    }
                    return `
                        <div class="board-entry ${typeClass}">
                            <div class="entry-meta">
                                <span class="entry-type">${e.type}</span>
                                <span>${e.timestamp}</span>
                            </div>
                            <pre>${escapeHtml(content)}</pre>
                        </div>
                    `;
                }).join('');
            } catch(err) {
                console.error(err);
            }
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        setInterval(fetchBoard, 1500);
        fetchBoard();
    </script>
</body>
</html>
"""


# For local debugging, you can run: uvicorn src.main:app --reload
