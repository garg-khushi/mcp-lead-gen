import sqlite3
import time
import random
import logging
from database import DB_NAME
import json
from datetime import datetime

LOG_FILE = "outreach.jsonl"

def log_event(event: dict):
    event = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **event,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    # Also print for terminal visibility
    print(event)

# Setup logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("outreach.log"),
#         logging.StreamHandler()
#     ]
# )

def send_email_smtp(to_email, subject, body):
    """
    Placeholder for real SMTP sending.
    For this assignment, we simulate success to avoid needing real credentials.
    To make it real, you would use smtplib with Gmail App Password.
    """
    # Simulate network delay
    time.sleep(0.5) 
    
    # Simulate occasional network failure for retry logic testing
    if random.random() < 0.1:  # 10% chance of failure
        raise Exception("SMTP Connection Timeout")
        
    return True

def process_outreach_batch(dry_run=True, limit=5):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get leads ready to send (MESSAGED status)
    cursor.execute("SELECT * FROM leads WHERE status='MESSAGED' LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    if not rows:
        logging.info("No messages waiting in queue.")
        conn.close()
        return

    logging.info(f"Starting batch of {len(rows)} messages. Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    
    for row in rows:
        lead = dict(row)
        lead_id = lead["id"]
        email = lead["email"]

        email_body = lead.get("message_email_a") or ""
        linkedin_body = lead.get("message_linkedin_a") or ""

        try:
            log_event({"level": "INFO", "stage": "send_outreach", "lead_id": lead_id, "email": email, "mode": "DRY_RUN" if dry_run else "LIVE", "event": "start_lead"})

            if dry_run:
                log_event({
                    "level": "INFO",
                    "stage": "send_outreach",
                    "lead_id": lead_id,
                    "email": email,
                    "event": "dry_run_preview",
                    "linkedin_url": lead.get("linkedin_url"),
                    "email_words": len(email_body.split()),
                    "linkedin_words": len(linkedin_body.split()),
                })
                # Do NOT update DB in dry-run
                continue

            max_retries = 2
            sent = False
            last_error = None

            for attempt in range(1, max_retries + 2):  # 1..3
                try:
                    log_event({"level": "INFO", "stage": "send_outreach", "lead_id": lead_id, "email": email, "event": "attempt", "attempt": attempt})

                    # Send Email (Simulated)
                    send_email_smtp(email, "Quick question", email_body)

                    # LinkedIn DM (Simulated)
                    # send_linkedin_dm(...)

                    sent = True
                    log_event({"level": "INFO", "stage": "send_outreach", "lead_id": lead_id, "email": email, "event": "attempt_success", "attempt": attempt})
                    break
                except Exception as e:
                    last_error = str(e)
                    log_event({"level": "WARN", "stage": "send_outreach", "lead_id": lead_id, "email": email, "event": "attempt_failed", "attempt": attempt, "error": last_error})
                    time.sleep(1)

            if sent:
                cursor.execute("UPDATE leads SET status='SENT', last_updated=datetime('now') WHERE id=?", (lead_id,))
                conn.commit()
                log_event({"level": "INFO", "stage": "send_outreach", "lead_id": lead_id, "email": email, "event": "lead_sent"})
            else:
                cursor.execute("UPDATE leads SET status='FAILED', last_updated=datetime('now') WHERE id=?", (lead_id,))
                conn.commit()
                log_event({"level": "ERROR", "stage": "send_outreach", "lead_id": lead_id, "email": email, "event": "lead_failed", "error": last_error})

            # Rate limit: 10/min = 6s per message
            log_event({"level": "INFO", "stage": "send_outreach", "lead_id": lead_id, "email": email, "event": "rate_limit_sleep", "seconds": 6})
            time.sleep(6)

        except Exception as e:
            log_event({"level": "ERROR", "stage": "send_outreach", "lead_id": lead_id, "email": email, "event": "critical_error", "error": str(e)})

    conn.close()
    logging.info("Batch processing complete.")

if __name__ == "__main__":
    # Test 1: Run a DRY RUN (Safe, no DB changes)
    print("--- STARTING DRY RUN ---")
    process_outreach_batch(dry_run=True, limit=3)
    
    # Test 2: Run a LIVE RUN (Updates DB, simulates sending)
    print("\n--- STARTING LIVE RUN ---")
    process_outreach_batch(dry_run=False, limit=3)