import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys
import os

# Ensure we point to the server.py file in the current directory
SERVER_SCRIPT = os.path.join(os.getcwd(), "server.py")

async def run_pipeline_step(dry_run: bool = True):

    # Connect to the MCP Server
    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # Step 1: Check Status
            # We call the 'get_pipeline_status' tool from our server
            status_result = await session.call_tool("get_pipeline_status")
            stats = status_result.content[0].text
            print(f"Current Pipeline Status: {stats}")
            
            # Parse the stats (comes back as string representation of dict)
            import ast
            stats_dict = ast.literal_eval(stats)
            
            # AGENT LOGIC: Decide what to do based on state hierarchy
            if stats_dict.get("NEW", 0) > 0:
                print("DECISION: Found NEW leads. Running enrichment...")
                await session.call_tool("enrich_leads", arguments={"mode": "offline"})
                return "Enrichment Triggered"
                
            elif stats_dict.get("ENRICHED", 0) > 0:
                print("DECISION: Found ENRICHED leads. Generating messages...")
                await session.call_tool("generate_messages")
                return "Message Generation Triggered"
                
            elif stats_dict.get("MESSAGED", 0) > 0:
                print("DECISION: Found MESSAGED leads. Sending outreach...")
                await session.call_tool("send_outreach", arguments={"dry_run": dry_run})
                return "Outreach Triggered"
            
            else:
                # If pipeline is empty or all sent/failed, generate more
                print("DECISION: Pipeline empty/finished. Generating new leads...")
                await session.call_tool("generate_leads", arguments={"amount": 10})
                return "New Leads Generated"
if __name__ == "__main__":
    # Default is dry-run. Use --live to actually send (SMTP if configured).
    dry_run = True
    if "--live" in sys.argv:
        dry_run = False

    asyncio.run(run_pipeline_step(dry_run=dry_run))
