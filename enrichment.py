import sqlite3
import json
import random
from database import DB_NAME

# Heuristic Data (Offline Mode Rules)
PAIN_POINTS = {
    "Technology": ["Legacy system integration", "High cloud infrastructure costs", "Developer retention"],
    "Healthcare": ["HIPAA compliance data silos", "Patient scheduling inefficiencies", "Rising supply costs"],
    "Finance": ["Regulatory reporting delays", "Data security threats", "Manual reconciliation errors"],
    "Retail": ["Inventory mismanagement", "Supply chain visibility", "Omnichannel consistency"],
    "Manufacturing": ["Equipment downtime", "Supply chain disruptions", "Quality control variability"]
}

TRIGGERS = [
    "Recently expanded to new region",
    "Hiring aggressively in engineering",
    "Published new quarterly report",
    "Announced strategic partnership",
    "New leadership appointment"
]

def enrich_offline(lead):
    """Rule-based enrichment using hardcoded industry patterns."""
    industry = lead['industry']
    
    # Estimate size (randomized for demo purposes)
    size = random.choice(["Small (1-50)", "Medium (51-500)", "Enterprise (500+)"])
    
    # Map industry to specific pain points
    pains = PAIN_POINTS.get(industry, ["Process inefficiency", "Cost optimization"])
    # Pick 2 random pain points
    selected_pains = random.sample(pains, min(2, len(pains)))
    
    enrichment = {
        "company_size": size,
        "persona": f"{lead['role']} - Decision Maker",
        "pain_points": selected_pains,
        "buying_triggers": [random.choice(TRIGGERS)],
        "confidence_score": random.randint(70, 95),
        "source": "offline_rules"
    }
    return enrichment

def enrich_ai(lead):
    """
    Simulates an AI enrichment call. 
    (Satisfies 'Mock Mode' requirement to avoid API keys for the demo).
    """
    # In a real app, you would call OpenAI here.
    # For now, we generate 'smarter' looking data to simulate AI.
    base_data = enrich_offline(lead) 
    base_data["source"] = "ai_mock"
    base_data["confidence_score"] = random.randint(85, 99) # AI is 'more confident'
    base_data["ai_insight"] = f"AI Analysis: {lead['company_name']} is likely prioritizing {base_data['pain_points'][0].lower()} to scale operations."
    
    return base_data

def process_enrichment_batch(mode="offline", limit=50):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Select leads that are currently NEW
    cursor.execute("SELECT * FROM leads WHERE status='NEW' LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    if not rows:
        print(f"No NEW leads found to enrich in {mode} mode.")
        conn.close()
        return

    print(f"Enriching {len(rows)} leads using {mode} mode...")
    
    for row in rows:
        lead = dict(row)
        
        if mode == "ai":
            data = enrich_ai(lead)
        else:
            data = enrich_offline(lead)
            
        # Update the lead in the database
        cursor.execute('''
            UPDATE leads 
            SET enrichment_data = ?, status = 'ENRICHED', last_updated = datetime('now')
            WHERE id = ?
        ''', (json.dumps(data), lead['id']))
        
    conn.commit()
    conn.close()
    print("Batch enrichment complete.")

if __name__ == "__main__":
    # We will enrich half with offline rules and half with AI mock
    process_enrichment_batch(mode="offline", limit=100)
    process_enrichment_batch(mode="ai", limit=100)