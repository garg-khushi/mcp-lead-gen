# 🚀 MCP-Powered Lead Generation, Enrichment & Outreach System

A full-stack, agent-driven demo system that uses the **Model Context Protocol (MCP)** to orchestrate lead generation, enrichment, personalized outreach, and delivery — with real-time monitoring via a frontend dashboard and workflow automation via **n8n**. This project demonstrates correct MCP tool usage, orchestration, state persistence, and safe outreach practices using only free and open-source tools.

---

## ✨ Key Features

- ✅ **MCP server** exposing structured tools (`generate_leads`, `enrich_leads`, `generate_messages`, `send_outreach`, `get_pipeline_status`).
- 🤖 **Agent-driven** decision making that advances leads through the pipeline based on current state.
- 🔁 **n8n workflow orchestration** via an HTTP bridge to the MCP server (preferred, but agent-only mode also supported).
- 🧠 **Offline + AI-style enrichment** modes sharing the same schema, with no paid APIs.
- ✉️ **A/B personalized email + LinkedIn DM** generation using configurable personas and targeting rules.
- 🛑 **Safe outreach** (dry-run by default) with rate limiting, retries, and simulated sending.
- 📊 **Real-time frontend monitoring** via Streamlit with pipeline metrics and controls.
- 💾 **Persistent state** via SQLite, including leads, enrichment, and outreach logs.
- 🧪 **Fully reproducible synthetic data generation** using Faker to generate ≥200 leads.

---

## 🏗️ System Architecture

The system is composed of an MCP server, an HTTP bridge, an async agent, an n8n workflow, a SQLite database, and a Streamlit dashboard.

```text
n8n Workflow
   │
   ▼
HTTP Request Nodes
   │
   ▼
MCP HTTP Bridge (FastAPI)
   │
   ▼
MCP Server (FastMCP)
   │
   ▼
Tools:
  generate_leads
  enrich_leads
  generate_messages
  send_outreach
  get_pipeline_status
   │
   ▼
SQLite (persistent state)
   │
   ▼
Streamlit Dashboard
📁 Project Structure
mcp-lead-gen/
├── agent.py          # Agent reasoning + MCP orchestration
├── server.py         # MCP server exposing tools
├── bridge_http.py    # HTTP → MCP bridge (FastAPI)
├── lead_gen.py       # Synthetic lead generation
├── enrichment.py     # Offline + AI-style enrichment
├── message_gen.py    # A/B message generation
├── sender.py         # Dry-run & live outreach sender
├── database.py       # SQLite schema + helpers
├── app.py            # Streamlit dashboard
├── config.json       # Targeting rules (industries/roles, personas)
├── n8n_workflow.json # Exported n8n workflow
├── outreach.jsonl    # Structured outreach logs
├── requirements.txt
├── .env.example
└── README.md
⚙️ Setup Instructions
1️⃣ Install dependencies
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

2️⃣ Initialize database
python database.py

2️⃣ Initialize database
bash
python database.py
Creates leads.db with full pipeline state tracking.

3️⃣ Start the MCP HTTP bridge
bash
uvicorn bridge_http:app --host 127.0.0.1 --port 8000
Health check:

bash
curl http://127.0.0.1:8000/health

4️⃣ Start the frontend dashboard
bash
streamlit run app.py
Open: http://localhost:8501

5️⃣ Start n8n
bash
n8n start
Open: http://localhost:5678

🔁 n8n Orchestration (MCP Workflow)
This project uses n8n to orchestrate the end-to-end MCP-powered lead pipeline.

Workflow Overview
The n8n workflow executes the following steps in order:

generate_leads – generates 200 synthetic but valid leads.

enrich_leads – enriches leads with personas, pain points, triggers.

generate_messages – creates A/B email and LinkedIn messages.

send_outreach – sends or simulates messages (dry-run by default).

Each HTTP Request node sends a POST request to the MCP HTTP bridge:
text
http://host.docker.internal:8000/tool
with a JSON body like:

json
{
  "tool": "generate_leads",
  "args": { "amount": 200 }
}
Importing the workflow
Open n8n.

Click Import workflow.

Select n8n_workflow.json.
Save and click Execute Workflow.

🤖 Agent-Driven Automation
The agent (agent.py) connects to the MCP server and decides the next action based on pipeline state.

State transitions:

EMPTY → generate_leads
NEW → enrich_leads

ENRICHED → generate_messages

MESSAGED → send_outreach

Run manually:

bash
python agent.py
The agent is also callable from the frontend via a Run Agent Step control.

🔌 MCP Tool Contracts
All tools use simple JSON contracts.

generate_leads

json
{ "amount": 200 }
enrich_leads

json
{ "mode": "offline" }
generate_messages

json
{}
send_outreach
json
{ "dry_run": true }
get_pipeline_status

json
{}
🧠 Enrichment Modes
Offline (rule-based)
Company size via heuristics.

Persona mapping (e.g., ICP roles, seniority).

Industry-specific pain points and buying triggers.

Confidence score from 0–100.

AI-style mode (mock / free)
Uses structured templates only (no paid APIs).

Produces the same schema as offline enrichment for easy swapping.

✉️ Outreach Safety
Outreach is designed to be safe and mocked by default.

Dry-run enabled by default for send_outreach.

No real LinkedIn automation; DMs are generated but not auto-sent.

Email sending is simulated, with optional SMTP test configuration.

Retry logic of at least 2 attempts for failed deliveries.

Rate limiting to max 10 messages per minute.
Structured JSON logs stored in outreach.jsonl.

📊 Frontend Dashboard
The Streamlit dashboard monitors and controls the pipeline in real time.

It displays:

Total leads, enriched leads, messages generated, messages sent, and failures.

Explicit queue stages and last action timestamp.

Live table view of leads and their current status.

Controls for Run pipeline, Run Agent Step, and Dry Run / Live Run toggle.
CSV export for leads and outreach logs.

🔐 Secrets & Safety
No secrets are committed to the repository.

.env.example documents the required environment variables.

All APIs are mocked or local; LinkedIn and email are simulated by default.


