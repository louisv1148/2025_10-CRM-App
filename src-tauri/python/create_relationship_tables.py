"""
Create relationship tables (LPPersonLink) if they don't exist
"""

import sqlite3
from database import DB_PATH, create_db_and_tables

def create_lppersonlink_table():
    """Create LPPersonLink table"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lppersonlink'")
    if cursor.fetchone():
        print("✓ LPPersonLink table already exists")
    else:
        cursor.execute("""
        CREATE TABLE lppersonlink (
            lp_id INTEGER NOT NULL,
            person_id INTEGER NOT NULL,
            PRIMARY KEY (lp_id, person_id),
            FOREIGN KEY(lp_id) REFERENCES lp (id),
            FOREIGN KEY(person_id) REFERENCES person (id)
        )
        """)
        print("✓ Created LPPersonLink table")

    conn.commit()
    conn.close()
    print("\n✓ Table creation complete!")


if __name__ == "__main__":
    print("Creating relationship tables...\n")
    # First ensure all tables exist
    create_db_and_tables()
    # Then create our specific table
    create_lppersonlink_table()
