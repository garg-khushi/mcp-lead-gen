from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

# Import your MCP tools directly (same functions the MCP server uses)
# Adjust these imports if your tool functions live elsewhere
from server import generate_leads, enrich_leads, generate_messages, send_outreach, get_pipeline_status

app = FastAPI(title="MCP HTTP Bridge", version="0.1")

class ToolCall(BaseModel):
    tool: str
    args: Optional[Dict[str, Any]] = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/tool")
def call_tool(payload: ToolCall):
    args = payload.args or {}
    try:
        if payload.tool == "generate_leads":
            return generate_leads(**args)
        if payload.tool == "enrich_leads":
            return enrich_leads(**args)
        if payload.tool == "generate_messages":
            return generate_messages(**args)
        if payload.tool == "send_outreach":
            return send_outreach(**args)
        if payload.tool in ("get_status", "get_metrics", "get_pipeline_status"):
            return get_pipeline_status(**args)

        raise HTTPException(status_code=400, detail=f"Unknown tool: {payload.tool}")
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Bad args for {payload.tool}: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
