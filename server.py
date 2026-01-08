from mcp.server.fastmcp import FastMCP
import sqlite3
from database import DB_NAME, add_leads
import lead_gen
import enrichment
import message_gen
import sender

# Initialize the MCP Server
mcp = FastMCP("Lead Gen System")

# @mcp.tool()
# def generate_leads(amount: int = 10, seed: int | None = None) -> str:
#     """
#     Generates a specific number of new leads and saves them to the database.
#     Args:
#         amount: Number of leads to generate (default 10)
#         seed: Optional random seed for reproducibility
#     """
#     leads = lead_gen.generate_leads(amount, seed=seed)
#     add_leads(leads)
#     return f"Successfully generated and saved {len(leads)} new leads."
@mcp.tool()
def generate_leads(amount: int = 10) -> str:
    """
    Tool: generate_leads
    Input schema:
    {
      "amount": number (required) — number of leads to generate
    }

    Output:
    {
      "message": string
    }

    Description:
    Generates synthetic but realistic B2B leads and persists them to SQLite.
    """

# @mcp.tool()
# def enrich_leads(mode: str = "offline") -> str:
#     """
#     Enriches pending leads with industry data.
#     Args:
#         mode: 'offline' (rule-based) or 'ai' (mock AI)
#     """
#     # Batch size of 50 for efficiency
#     enrichment.process_enrichment_batch(mode=mode, limit=50)
#     return f"Batch enrichment complete using {mode} mode."
@mcp.tool()
def enrich_leads(mode: str = "offline") -> str:
    """
    Tool: enrich_leads
    Input schema:
    {
      "mode": "offline" | "ai"
    }

    Output:
    {
      "message": string
    }

    Description:
    Enriches NEW leads with personas, company size, pain points, triggers, and confidence score.
    """

# @mcp.tool()
# def generate_messages() -> str:
#     """
#     Generates A/B variations of emails and LinkedIn DMs for enriched leads.
#     """
#     message_gen.generate_messages_batch(limit=50)
#     return "Message generation complete for pending enriched leads."

@mcp.tool()
def generate_messages() -> str:
    """
    Tool: generate_messages
    Input schema: {}

    Output:
    {
      "message": string
    }

    Description:
    Generates A/B variants of email and LinkedIn messages using enriched lead data.
    """


# @mcp.tool()
# def send_outreach(dry_run: bool = True) -> str:
#     """
#     Sends the generated messages.
#     Args:
#         dry_run: If True, logs the output without sending. If False, updates status to SENT.
#     """
#     sender.process_outreach_batch(dry_run=dry_run, limit=10)
#     return f"Outreach batch complete. Dry Run: {dry_run}"

@mcp.tool()
def send_outreach(dry_run: bool = True) -> str:
    """
    Tool: send_outreach
    Input schema:
    {
      "dry_run": boolean
    }

    Output:
    {
      "message": string
    }

    Description:
    Sends or simulates outreach with retry logic, rate limiting, and structured logging.
    """


# @mcp.tool()
# def get_pipeline_status() -> dict:
#     """
#     Returns the count of leads at each stage of the pipeline.
#     Useful for monitoring progress.
#     """
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
    
#     statuses = ["NEW", "ENRICHED", "MESSAGED", "SENT", "FAILED"]
#     stats = {}
#     @mcp.tool()
#     def get_status() -> dict:
#         """
#         Alias for get_pipeline_status (spec-compliant name).
#         """
#         return get_pipeline_status()
    
#     for status in statuses:
#         cursor.execute("SELECT COUNT(*) FROM leads WHERE status = ?", (status,))
#         stats[status] = cursor.fetchone()[0]
        
#     conn.close()
#     return stats

@mcp.tool()
def get_pipeline_status() -> dict:
    """
    Tool: get_pipeline_status
    Input schema: {}

    Output:
    {
      "NEW": number,
      "ENRICHED": number,
      "MESSAGED": number,
      "SENT": number,
      "FAILED": number
    }

    Description:
    Returns real-time pipeline counts for frontend and orchestration.
    """


if __name__ == "__main__":
    # Runs the server
    mcp.run()