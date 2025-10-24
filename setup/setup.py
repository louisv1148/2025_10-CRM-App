"""
Database initialization script for CRM Meeting App
Creates database schema and seeds example data
"""

import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join("db", "crm.db")
SCHEMA_PATH = os.path.join("src-tauri", "python", "schema.sql")

# Create directories
os.makedirs("db", exist_ok=True)
os.makedirs("data/recordings", exist_ok=True)
os.makedirs("data/transcripts", exist_ok=True)
os.makedirs("data/summaries", exist_ok=True)

print("📂 Creating database directories...")

# Create database and schema
print(f"🗄️  Creating database at {DB_PATH}...")
with sqlite3.connect(DB_PATH) as conn:
    # Read and execute schema
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
        conn.executescript(schema)

    print("✓ Schema created")

    # Seed example data
    print("🌱 Seeding example data...")

    # Example LPs
    conn.execute("INSERT INTO lp (name) VALUES ('Example LP Fund')")
    conn.execute("INSERT INTO lp (name) VALUES ('Demo Capital Partners')")

    # Example GPs
    conn.execute("INSERT INTO gp (name) VALUES ('Example GP Ventures')")
    conn.execute("INSERT INTO gp (name) VALUES ('Demo Growth Fund')")

    # Example People
    conn.execute("""
        INSERT INTO person (name, role, org_type, org_id, email, phone)
        VALUES ('John Smith', 'Partner', 'LP', 1, 'john@example.com', '555-0100')
    """)
    conn.execute("""
        INSERT INTO person (name, role, org_type, org_id, email, phone)
        VALUES ('Jane Doe', 'Managing Partner', 'GP', 1, 'jane@demo.com', '555-0200')
    """)

    # Example Note
    conn.execute("""
        INSERT INTO note (date, lp_id, gp_id, raw_notes, summary, fundraise, interest)
        VALUES (?, 1, 1,
            'Discussed Q4 investment strategy. Strong interest in healthcare sector. Follow up needed on due diligence timeline.',
            'Productive meeting about Q4 strategy with focus on healthcare investments.',
            'Series A',
            'Hot')
    """, (datetime.now().isoformat(),))

    # Example Todos
    note_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.execute("""
        INSERT INTO todo (note_id, description, status)
        VALUES (?, 'Send due diligence checklist', 'pending')
    """, (note_id,))
    conn.execute("""
        INSERT INTO todo (note_id, description, status)
        VALUES (?, 'Schedule follow-up call for next week', 'pending')
    """, (note_id,))

    conn.commit()
    print("✓ Example data seeded")

print("")
print("✅ Database and folders ready!")
print(f"📍 Database location: {os.path.abspath(DB_PATH)}")
print("")
print("You can now:")
print("  - View data: sqlite3 db/crm.db '.tables'")
print("  - Start backend: python3 src-tauri/python/backend.py")
print("  - Run app: npm run tauri:dev")
