# IT INCIDENT RESPONSE WAR‑ROOM

A **Semantic‑Kernel‑powered** multi‑agent system that demonstrates a production‑ready blackboard (war‑room) architecture for automated incident response.

## Architecture
- **IncidentBoard** – thread‑safe blackboard where agents post and read information.
- **Agents** (each runs in its own daemon thread)
  - `AlertAgent` – receives an incident alert.
  - `LogsAgent` – fetches recent logs (simulated).
  - `DependencyAgent` – discovers upstream/downstream services.
  - `MitigationAgent` – proposes a mitigation based on severity, logs and dependencies.
  - `CommanderAgent` – decides the final action, records the decision and generates a markdown **timeline**.
  - `CommsAgent` – drafts a status‑page update for the incident.
- **FastAPI HTTP API** – external entry point:
  - `POST /alert` – submit an incident.
  - `GET /board` – retrieve the current board entries.
- **Semantic Kernel** – optional LLM integration (`src/kernel_init.py`). If `OPENAI_API_KEY` is set the kernel can be used by agents for richer reasoning.

## Quick start
```bash
# 1️⃣ Clone / open this folder
cd C:\Users\phani\Downloads\ca-2-

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run the API (background task)
uvicorn src.main:app --host 127.0.0.1 --port 8000
```
The server will start the background agents (except `AlertAgent`, which is created per request).

### Send an incident
```bash
curl -X POST http://127.0.0.1:8000/alert \
  -H "Content-Type: application/json" \
  -d '{"service":"service-a","symptom":"high latency","severity":"high"}'
```
The system will automatically progress through the workflow. You can inspect the result:
```bash
curl http://127.0.0.1:8000/board
```
You will see a list of entries ending with a `timeline` markdown snippet and a `status` update.

## Running the demo script
```bash
python run_demo.py
```
The script starts the background agents, posts a demo alert, waits a few seconds and prints the board.

## Testing
```bash
pip install pytest
pytest
```
See the `tests/` folder for unit‑tests covering the board and the core agents.

## Docker (optional)
A minimal Dockerfile is provided for containerised deployment.
```bash
docker build -t incident‑war‑room .
docker run -p 8000:8000 incident‑war‑room
```

## Extending the system
- Plug in a real LLM via `kernel_init.py` and let agents call `kernel` for more sophisticated reasoning.
- Replace the mock log retrieval with real log‑collector integration (e.g., ELK, Splunk).
- Add persistence (e.g., SQLite) to the board for post‑mortem storage.
- Implement authentication/authorization for the API.

---
*This project was built autonomously using the Antigravity AI coding assistant.*
