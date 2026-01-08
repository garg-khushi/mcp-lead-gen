import streamlit as st
import sqlite3
import pandas as pd
import subprocess
import time
import json
import os
import plotly.graph_objects as go
import plotly.express as px
from database import DB_NAME

st.set_page_config(page_title="MCP Lead Gen Dashboard", layout="wide")

# --- Tabs for Navigation ---
tab_dashboard, tab_settings = st.tabs(["📊 Dashboard", "⚙️ Settings & Targeting"])

def get_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM leads", conn)
    conn.close()
    return df

def get_stats(df):
    stats = {
        "Total": len(df),
        "New": len(df[df['status'] == 'NEW']),
        "Enriched": len(df[df['status'] == 'ENRICHED']),
        "Messaged": len(df[df['status'] == 'MESSAGED']),
        "Sent": len(df[df['status'] == 'SENT']),
        "Failed": len(df[df['status'] == 'FAILED'])
    }
    return stats

# ==========================
# TAB 1: DASHBOARD
# ==========================
with tab_dashboard:
    st.title("🚀 MCP-Powered Lead Gen Pipeline")

    # Sidebar
    st.sidebar.header("Actions")
    if st.sidebar.button("▶️ Run Agent Step"):
        with st.spinner("Agent is reasoning and executing..."):
            result = subprocess.run(["python", "agent.py"], capture_output=True, text=True)
            if result.returncode == 0:
                st.sidebar.success("Agent Step Complete!")
                with st.sidebar.expander("See Agent Logs"):
                    st.code(result.stdout)
            else:
                st.sidebar.error("Agent Failed")
                st.sidebar.error(result.stderr)
        time.sleep(1)
        st.rerun()
        if st.sidebar.button("🚀 Run Full Pipeline"):
            with st.spinner("Running full pipeline: generate → enrich → message → send"):
                cmds = [
                    ["python", "-c", "from lead_gen import generate_leads; from database import init_db, add_leads; init_db(); add_leads(generate_leads(count=200, seed=42))"],
                    ["python", "enrichment.py"],
                    ["python", "message_gen.py"],
            ]

            # Send step: dry-run vs live-run
                if run_mode == "Dry Run":
                    cmds.append(["python", "-c", "from sender import send_outreach_batch; send_outreach_batch(limit=200, dry_run=True)"])
                else:
                    cmds.append(["python", "-c", "from sender import send_outreach_batch; send_outreach_batch(limit=200, dry_run=False)"])

            logs = []
            ok = True
            for cmd in cmds:
                result = subprocess.run(cmd, capture_output=True, text=True)
                logs.append({"cmd": " ".join(cmd), "stdout": result.stdout, "stderr": result.stderr, "code": result.returncode})
                if result.returncode != 0:
                    ok = False
                    break

            if ok:
                st.sidebar.success("Full Pipeline Complete!")
            else:
                st.sidebar.error("Full Pipeline Failed")

            with st.sidebar.expander("See Pipeline Logs"):
                st.json(logs)

        time.sleep(1)
        st.rerun()

    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("Export")
    st.sidebar.header("Actions")
    run_mode = st.sidebar.radio("Run Mode", ["Dry Run", "Live Run"], index=0)
    st.sidebar.caption("Dry Run = no real sending; Live Run = SMTP send (if configured).")

    try:
        csv_data = get_data().to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="leads_export.csv",
            mime="text/csv"
        )
    except Exception:
        st.sidebar.warning("No data to export yet.")

    # Metrics & Visuals
    df = get_data()
    if not df.empty:
        stats = get_stats(df)
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Leads", stats["Total"])
        col2.metric("Enriched", stats["Enriched"])
        col3.metric("Ready to Send", stats["Messaged"])
        col4.metric("Sent (Live)", stats["Sent"])
        col5.metric("Failed", stats["Failed"])

        st.markdown("---")
        
        if stats["Total"] > 0:
            progress = stats["Sent"] / stats["Total"]
        else:
            progress = 0
        st.write("### Pipeline Progress (Sent)")
        st.progress(progress)

        st.markdown("---")
        
        col_table, col_graph = st.columns([2, 1])
        
        with col_table:
            st.write("### 📋 Lead Database")
            display_cols = ['full_name', 'company_name', 'role', 'status', 'email']
            st.dataframe(df[display_cols], use_container_width=True)

        with col_graph:
            st.write("### Status Distribution")
            # Create a professional Donut Chart using Plotly
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig = px.pie(
                status_counts, 
                values='Count', 
                names='Status', 
                hole=0.4, # Makes it a Donut
                color='Status',
                color_discrete_map={
                    "NEW": "#3498db",       # Blue
                    "ENRICHED": "#f1c40f",  # Yellow
                    "MESSAGED": "#e67e22",  # Orange
                    "SENT": "#2ecc71",      # Green
                    "FAILED": "#e74c3c"     # Red
                }
            )
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Database is empty. Run the Agent to generate leads.")

# ==========================
# TAB 2: SETTINGS (BONUS)
# ==========================
with tab_settings:
    st.header("🎯 Target Personas Configuration")
    st.write("Edit the JSON below to configure which Industries and Roles the generator targets.")
    
    CONFIG_FILE = "config.json"
    
    # Load current config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            current_config = f.read()
    else:
        current_config = "{}"

    # Editor
    new_config = st.text_area("Targeting Rules (JSON)", current_config, height=300)
    
    if st.button("💾 Save Configuration"):
        try:
            # Validate JSON before saving
            json_object = json.loads(new_config)
            with open(CONFIG_FILE, "w") as f:
                f.write(new_config)
            st.success("Configuration saved! Future leads will use these rules.")
        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please correct it.")