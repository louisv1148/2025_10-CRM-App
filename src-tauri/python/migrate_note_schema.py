#!/usr/bin/env python3
"""
Migrate Note table schema to support Notion imports with many-to-many relationships.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../db/crm.db")


def migrate_note_table():
    """Add new columns to Note table and create relationship link tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Migrating Note table...")

    # New columns to add to Note table
    new_columns = [
        ("notion_id", "VARCHAR"),
        ("name", "VARCHAR"),
        ("contact_type", "VARCHAR"),
        ("local_mf", "VARCHAR"),
        ("local_alts", "VARCHAR"),
        ("intl_mf", "VARCHAR"),
        ("intl_alts", "VARCHAR"),
        ("roadshows", "VARCHAR"),
        ("pin", "VARCHAR"),
        ("useful", "INTEGER"),  # Boolean as INTEGER
        ("ai_summary", "VARCHAR"),
        ("content_text", "VARCHAR"),
        ("content_json", "VARCHAR"),
        ("image_paths", "VARCHAR"),
    ]

    # Check which columns already exist
    cursor.execute("PRAGMA table_info(note)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Add missing columns
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            print(f"  Adding column: {col_name}")
            sql = f"ALTER TABLE note ADD COLUMN {col_name} {col_type}"
            cursor.execute(sql)

    # Create index on notion_id if it doesn't exist
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_note_notion_id ON note(notion_id)
    """)

    # Create Note-GP link table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notegplink (
            note_id INTEGER NOT NULL,
            gp_id INTEGER NOT NULL,
            PRIMARY KEY (note_id, gp_id),
            FOREIGN KEY (note_id) REFERENCES note(id),
            FOREIGN KEY (gp_id) REFERENCES gp(id)
        )
    """)
    print("  Created NoteGPLink table (if not exists)")

    # Create Note-LP link table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notelplink (
            note_id INTEGER NOT NULL,
            lp_id INTEGER NOT NULL,
            PRIMARY KEY (note_id, lp_id),
            FOREIGN KEY (note_id) REFERENCES note(id),
            FOREIGN KEY (lp_id) REFERENCES lp(id)
        )
    """)
    print("  Created NoteLPLink table (if not exists)")

    # Create Note-Distributor link table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notedistributorlink (
            note_id INTEGER NOT NULL,
            distributor_id INTEGER NOT NULL,
            PRIMARY KEY (note_id, distributor_id),
            FOREIGN KEY (note_id) REFERENCES note(id),
            FOREIGN KEY (distributor_id) REFERENCES distributor(id)
        )
    """)
    print("  Created NoteDistributorLink table (if not exists)")

    conn.commit()
    conn.close()

    print("\nMigration complete!")


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Please run database.py first to create the database.")
        exit(1)

    migrate_note_table()
