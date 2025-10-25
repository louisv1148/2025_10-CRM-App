"""
Fix Person table to make legacy fields nullable
SQLite requires recreating the table to change constraints
"""

import sqlite3
from database import DB_PATH

def fix_person_table():
    """Recreate Person table with nullable legacy fields"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Fixing Person table constraints...\n")

    # Step 1: Create new table with correct schema
    cursor.execute("""
    CREATE TABLE person_new (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR NOT NULL,
        cell_phone VARCHAR,
        office_phone VARCHAR,
        email VARCHAR,
        location VARCHAR,
        position VARCHAR,
        people_type VARCHAR,
        personal_note VARCHAR,
        role VARCHAR,  -- Made nullable
        org_type VARCHAR,  -- Made nullable
        org_id INTEGER,
        phone VARCHAR  -- Old field, keep for compatibility
    )
    """)
    print("✓ Created new person table")

    # Step 2: Copy data from old table
    cursor.execute("""
    INSERT INTO person_new (id, name, role, org_type, org_id, email, phone,
                            cell_phone, office_phone, location, position,
                            people_type, personal_note)
    SELECT id, name, role, org_type, org_id, email, phone,
           cell_phone, office_phone, location, position,
           people_type, personal_note
    FROM person
    """)
    print("✓ Copied data from old table")

    # Step 3: Drop old table
    cursor.execute("DROP TABLE person")
    print("✓ Dropped old table")

    # Step 4: Rename new table
    cursor.execute("ALTER TABLE person_new RENAME TO person")
    print("✓ Renamed new table to person")

    conn.commit()
    conn.close()
    print("\n✓ Migration complete!")


if __name__ == "__main__":
    fix_person_table()
