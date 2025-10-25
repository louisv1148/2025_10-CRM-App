"""
Migrate LP table to add new columns from Notion schema
Preserves existing data
"""

import sqlite3
import os
from database import DB_PATH

def migrate_lp_table():
    """Add new columns to LP table"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # List of new columns to add
    new_columns = [
        ("aum_billions", "REAL"),
        ("advisor", "VARCHAR"),
        ("intl_alts", "VARCHAR"),
        ("intl_mf", "VARCHAR"),
        ("local_alts", "VARCHAR"),
        ("local_mf", "VARCHAR"),
        ("investment_high", "REAL"),
        ("investment_low", "REAL"),
        ("location", "VARCHAR"),
        ("priority", "VARCHAR"),
        ("type_of_group", "VARCHAR"),
        ("text", "VARCHAR"),
    ]

    # Check which columns already exist
    cursor.execute("PRAGMA table_info(lp)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Add missing columns
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                sql = f"ALTER TABLE lp ADD COLUMN {col_name} {col_type}"
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
    print("Migrating LP table schema...\n")
    migrate_lp_table()
