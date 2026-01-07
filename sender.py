import sqlite3
import time
import random
import logging
from database import DB_NAME

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("outreach.log"),
        logging.StreamHandler()
    ]
)

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
        
        try:
            logging.info(f"Processing lead: {lead['email']}")
            
            if dry_run:
                # Dry Run: Just log what would happen
                logging.info(f"[DRY RUN] Would send email to {lead['email']}")
                logging.info(f"[DRY RUN] Would send LinkedIn DM to {lead['linkedin_url']}")
            else:
                # Live Mode: Attempt to send with Retries
                max_retries = 2
                sent = False
                
                for attempt in range(max_retries + 1):
                    try:
                        # Send Email (Simulated)
                        send_email_smtp(lead['email'], "Subject Here", lead['message_email'])
                        
                        # Send LinkedIn (Simulated)
                        # send_linkedin_dm(...) 
                        
                        sent = True
                        break # Success, exit retry loop
                    except Exception as e:
                        logging.warning(f"Attempt {attempt+1} failed for {lead['email']}: {e}")
                        time.sleep(1) # Backoff before retry
                
                if sent:
                    cursor.execute("UPDATE leads SET status='SENT', last_updated=datetime('now') WHERE id=?", (lead['id'],))
                    logging.info(f"Successfully sent to {lead['email']}")
                else:
                    cursor.execute("UPDATE leads SET status='FAILED', last_updated=datetime('now') WHERE id=?", (lead['id'],))
                    logging.error(f"Failed to send to {lead['email']} after retries")
                
                conn.commit()
                
                # Rate Limiting: Max 10 per minute = 1 every 6 seconds
                # We sleep here to enforce it
                logging.info("Rate limit sleep (6s)...")
                time.sleep(6)
                
        except Exception as e:
            logging.error(f"Critical error processing lead {lead['id']}: {e}")

    conn.close()
    logging.info("Batch processing complete.")

if __name__ == "__main__":
    # Test 1: Run a DRY RUN (Safe, no DB changes)
    print("--- STARTING DRY RUN ---")
    process_outreach_batch(dry_run=True, limit=3)
    
    # Test 2: Run a LIVE RUN (Updates DB, simulates sending)
    print("\n--- STARTING LIVE RUN ---")
    process_outreach_batch(dry_run=False, limit=3)