"""
Migrate Person table to add new columns from Notion schema
Preserves existing data
"""

import sqlite3
from database import DB_PATH

def migrate_person_table():
    """Add new columns to Person table"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # List of new columns to add
    new_columns = [
        ("cell_phone", "VARCHAR"),
        ("office_phone", "VARCHAR"),
        ("location", "VARCHAR"),
        ("position", "VARCHAR"),
        ("people_type", "VARCHAR"),
        ("personal_note", "VARCHAR"),
    ]

    # Check which columns already exist
    cursor.execute("PRAGMA table_info(person)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Add missing columns
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                sql = f"ALTER TABLE person ADD COLUMN {col_name} {col_type}"
                cursor.execute(sql)
                print(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"✗ Could not add {col_name}: {e}")
        else:
            print(f"  Column {col_name} already exists")

    conn.commit()
    conn.close()
    print("\n✓ Migration complete!")


if __name__ == "__main__":
    print("Migrating Person table schema...\n")
    migrate_person_table()
