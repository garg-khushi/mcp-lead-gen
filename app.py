import streamlit as st
import sqlite3
import pandas as pd
import subprocess
import time
import json
import os
import plotly.express as px
from database import DB_NAME

st.set_page_config(page_title="MCP Lead Gen Dashboard", layout="wide")

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

# Sidebar (actions / export)
st.sidebar.header("Actions")

run_mode = st.sidebar.radio(
    "Run Mode",
    ["Dry Run", "Live Run"],
    index=0,
    key="run_mode"
)
st.sidebar.caption("Dry Run = logs only; Live Run = updates DB to SENT/FAILED (SMTP if configured).")

if st.sidebar.button("▶️ Run Agent Step"):
    with st.spinner("Agent is reasoning and executing..."):
        cmd = ["python", "agent.py"]
        if run_mode == "Live Run":
            cmd.append("--live")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            st.sidebar.success("Agent Step Complete!")
            with st.sidebar.expander("See Agent Logs"):
                st.code(result.stdout)
        else:
            st.sidebar.error("Agent Failed")
            st.sidebar.error(result.stderr)

    time.sleep(1)
    st.rerun()

if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("Export")

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

# --- Tabs for Navigation ---
tab_dashboard, tab_settings = st.tabs(["📊 Dashboard", "⚙️ Settings & Targeting"])

# ==========================
# TAB 1: DASHBOARD
# ==========================
with tab_dashboard:
    st.title("🚀 MCP-Powered Lead Gen Pipeline")

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
        st.markdown("### 🧵 Queue Status (Pipeline Stages)")

        q1, q2, q3 = st.columns(3)
        q1.metric("🟦 Ingestion Queue (NEW)", stats["New"])
        q2.metric("🟨 Processing Queue (ENRICHED)", stats["Enriched"])
        q3.metric("🟧 Dispatch Queue (MESSAGED)", stats["Messaged"])

        st.markdown("---")
        
        progress = stats["Sent"] / stats["Total"] if stats["Total"] > 0 else 0
        progress = max(0.0, min(1.0, progress))
        st.write("### Pipeline Progress (Sent)")
        st.progress(progress)

        st.markdown("---")
        
        col_table, col_graph = st.columns([2, 1])
        
        with col_table:
            st.write("### 📋 Lead Database")
            # Show "Last Action" safely (works even if DB column is missing)
            if "last_updated" in df.columns:
                df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
                df["last_action"] = df["last_updated"].dt.strftime("%Y-%m-%d %H:%M:%S")
                sort_col = "last_updated"
            else:
                df["last_action"] = ""
                sort_col = None

            display_cols = ["full_name", "company_name", "role", "status", "last_action", "email"]
            table_df = df[display_cols]
            if sort_col:
                table_df = table_df.join(df[[sort_col]]).sort_values(by=sort_col, ascending=False).drop(columns=[sort_col])

            st.dataframe(table_df, use_container_width=True)

            # Make last_updated readable + show as "Last Action"
            # df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
            # df["last_action"] = df["last_updated"].dt.strftime("%Y-%m-%d %H:%M:%S")

            # display_cols = ["full_name", "company_name", "role", "status", "last_action", "email"]
            # st.dataframe(df[display_cols].sort_values(by="last_updated", ascending=False), use_container_width=True)
            # display_cols = ['full_name', 'company_name', 'role', 'status', 'email']
            # guard against missing columns
            # available_cols = [c for c in display_cols if c in df.columns]
            # st.dataframe(df[available_cols], use_container_width=True)

        with col_graph:
            st.write("### Status Distribution")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig = px.pie(
                status_counts, 
                values='Count', 
                names='Status', 
                hole=0.4,
                color='Status',
                color_discrete_map={
                    "NEW": "#3498db",
                    "ENRICHED": "#f1c40f",
                    "MESSAGED": "#e67e22",
                    "SENT": "#2ecc71",
                    "FAILED": "#e74c3c"
                }
            )
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Database is empty. Run the Agent to generate leads.")

# ==========================
# TAB 2: SETTINGS
# ==========================
with tab_settings:
    st.header("🎯 Target Personas Configuration")
    st.write("Edit the JSON below to configure which Industries and Roles the generator targets.")
    
    CONFIG_FILE = "config.json"
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            current_config = f.read()
    else:
        current_config = "{}"

    new_config = st.text_area("Targeting Rules (JSON)", current_config, height=300)
    
    if st.button("💾 Save Configuration"):
        try:
            json.loads(new_config)  # validate
            with open(CONFIG_FILE, "w") as f:
                f.write(new_config)
            st.success("Configuration saved! Future leads will use these rules.")
        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please correct it.")