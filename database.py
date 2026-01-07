import sqlite3
import json
from datetime import datetime

DB_NAME = "leads.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Added UNIQUE constraint to email
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            company_name TEXT,
            role TEXT,
            industry TEXT,
            website TEXT,
            email TEXT UNIQUE, 
            linkedin_url TEXT,
            country TEXT,
            status TEXT DEFAULT 'NEW',
            enrichment_data TEXT,
            message_email TEXT,
            message_linkedin TEXT,
            last_updated TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized (Strict Mode).")

def add_leads(leads_list):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    count = 0
    for lead in leads_list:
        try:
            # Use INSERT OR IGNORE to skip duplicates gracefully
            cursor.execute('''
                INSERT OR IGNORE INTO leads (full_name, company_name, role, industry, website, email, linkedin_url, country, status, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead['full_name'], lead['company_name'], lead['role'], lead['industry'], 
                lead['website'], lead['email'], lead['linkedin_url'], lead['country'], 
                'NEW', datetime.now()
            ))
            if cursor.rowcount > 0:
                count += 1
        except sqlite3.Error as e:
            print(f"Error adding lead: {e}")
            
    conn.commit()
    conn.close()
    print(f"Added {count} new leads to database (duplicates skipped).")
    """Initialize the SQLite database with the required schema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create leads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            company_name TEXT,
            role TEXT,
            industry TEXT,
            website TEXT,
            email TEXT,
            linkedin_url TEXT,
            country TEXT,
            status TEXT DEFAULT 'NEW',
            enrichment_data TEXT,
            message_email TEXT,
            message_linkedin TEXT,
            last_updated TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized.")


def get_leads_by_status(status):
    """Retrieve leads filtering by status."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM leads WHERE status = ?", (status,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()