## 🔁 n8n Orchestration (MCP Workflow)

This project uses **n8n** to orchestrate the end-to-end MCP-powered lead pipeline.

### Workflow Overview
The n8n workflow executes the following steps in order:

1. `generate_leads` – generates 200 synthetic but valid leads
2. `enrich_leads` – enriches leads with personas, pain points, triggers
3. `generate_messages` – creates A/B email and LinkedIn messages
4. `send_outreach` – sends messages (dry-run by default)

### How it Works
- n8n triggers HTTP requests to a local MCP HTTP bridge
- The bridge forwards requests to MCP tools
- Lead state is persisted in SQLite across stages

### How to Run
1. Start the MCP HTTP bridge:
   ```bash
   uvicorn bridge_http:app --host 127.0.0.1 --port 8000
