import sqlite3
import json
import random
from database import DB_NAME

# A/B Templates for Email
EMAIL_TEMPLATES = {
    "A": """Subject: Question about {company} strategy

Hi {first_name},

Saw you're leading operations at {company}.

Given the shift in {industry}, are you currently dealing with {pain_point}? Many {role}s I speak to are focused on this right now.

We help companies address exactly this using our new automated workflow.

Worth a 15-minute chat next Tuesday?

Best,
[Your Name]""",

    "B": """Subject: {pain_point} at {company}?

Hi {first_name},

I'm reaching out because I see you are the {role} at {company}.

My team has been researching the {industry} space and noticed that {pain_point} is a major bottleneck for teams of your size ({size}).

We have a solution that directly solves this.

Open to a brief call to discuss?

Cheers,
[Your Name]"""
}

# A/B Templates for LinkedIn
LINKEDIN_TEMPLATES = {
    "A": """Hi {first_name}, saw your work at {company}. Are you feeling the impact of {pain_point}? We help {industry} leaders solve this. Let's connect.""",
    
    "B": """Hey {first_name}, impressive tenure as {role}. I'm curious if {pain_point} is on your radar for Q4? I'd love to share how we fix that."""
}
def assert_word_limit(text, max_words, label):
    words = len(text.split())
    if words > max_words:
        raise ValueError(f"{label} exceeds {max_words} words ({words})")

def generate_messages_batch(limit=50):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get leads that are ENRICHED but not yet MESSAGED
    cursor.execute("SELECT * FROM leads WHERE status='ENRICHED' LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    if not rows:
        print("No ENRICHED leads found to message.")
        conn.close()
        return

    print(f"Generating messages for {len(rows)} leads...")
    
    for row in rows:
        lead = dict(row)
        enrichment = json.loads(lead['enrichment_data'])
        
        # Extract data for templates
        first_name = lead['full_name'].split()[0]
        pain_point = enrichment['pain_points'][0] if enrichment['pain_points'] else "efficiency"
        
        # Select Random Variation (A/B Test)
        # email_variant = random.choice(["A", "B"])
        # linkedin_variant = random.choice(["A", "B"])
        
        # Fill Email Template
        email_a = EMAIL_TEMPLATES["A"].format(
            first_name=first_name,
            company=lead['company_name'],
            industry=lead['industry'],
            role=lead['role'],
            pain_point=pain_point.lower(),
            size=enrichment.get('company_size', 'growing')
        )

        email_b = EMAIL_TEMPLATES["B"].format(
            first_name=first_name,
            company=lead['company_name'],
            industry=lead['industry'],
            role=lead['role'],
            pain_point=pain_point.lower(),
            size=enrichment.get('company_size', 'growing')
        )

        
        # Fill LinkedIn Template
        linkedin_a = LINKEDIN_TEMPLATES["A"].format(
            first_name=first_name,
            company=lead['company_name'],
            industry=lead['industry'],
            role=lead['role'],
            pain_point=pain_point.lower()
        )

        linkedin_b = LINKEDIN_TEMPLATES["B"].format(
            first_name=first_name,
            company=lead['company_name'],
            industry=lead['industry'],
            role=lead['role'],
            pain_point=pain_point.lower()
        )

        assert_word_limit(email_a, 120, "Email A")
        assert_word_limit(email_b, 120, "Email B")
        assert_word_limit(linkedin_a, 60, "LinkedIn A")
        assert_word_limit(linkedin_b, 60, "LinkedIn B")

        # Update DB
        cursor.execute('''
            UPDATE leads
            SET
                message_email_a = ?,
                message_email_b = ?,
                message_linkedin_a = ?,
                message_linkedin_b = ?,
                status = 'MESSAGED',
                last_updated = datetime('now')
            WHERE id = ?
        ''', (email_a, email_b, linkedin_a, linkedin_b, lead['id']))

        
    conn.commit()
    conn.close()
    print("Message generation complete.")

if __name__ == "__main__":
    # Generate messages for all 200 enriched leads
    generate_messages_batch(limit=200)