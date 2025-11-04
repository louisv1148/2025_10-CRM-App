"""
Migrate Distributor table to add new columns
Preserves existing data
"""

import sqlite3
from database import DB_PATH, create_db_and_tables

def migrate_distributor_table():
    """Add new columns to Distributor table and create DistributorPersonLink"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add columns to Distributor table
    new_columns = [
        ("headquarter", "VARCHAR"),
        ("mexico", "VARCHAR"),
        ("text", "VARCHAR"),
    ]

    # Check which columns already exist
    cursor.execute("PRAGMA table_info(distributor)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Add missing columns
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                sql = f"ALTER TABLE distributor ADD COLUMN {col_name} {col_type}"
                cursor.execute(sql)
                print(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"✗ Could not add {col_name}: {e}")
        else:
            print(f"  Column {col_name} already exists")

    conn.commit()
    conn.close()

    # Create DistributorPersonLink table using SQLModel
    print("\n✓ Creating DistributorPersonLink table...")
    create_db_and_tables()

    print("\n✓ Migration complete!")


if __name__ == "__main__":
    print("Migrating Distributor table schema...\n")
    migrate_distributor_table()
