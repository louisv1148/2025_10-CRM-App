"""
Simple GP import from Notion CSV - Core fields only, no relationships
"""

import csv
import os
import shutil
from database import GP, create_db_and_tables, get_session, engine, DB_PATH
from sqlmodel import Session

def import_gps_simple(csv_path: str):
    """Import GP data from Notion CSV - core fields only"""

    with Session(engine) as session:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                gp_name = row['Name'].strip()
                if not gp_name:
                    continue

                print(f"Importing GP: {gp_name}")

                # Create GP with core fields only
                gp = GP(
                    name=gp_name,
                    location=row.get('Location', '').strip() or None,
                    contact_level=row.get('Contact Level', '').strip() or None,
                    flagship_strategy=row.get('Flagship', '').strip() or None,
                    other_strategies=row.get('Others', '').strip() or None,
                    note=row.get('Note', '').strip() or None,
                    # Skip distributor_id for now
                )
                session.add(gp)
                count += 1

        session.commit()
        print(f"\n✓ Import complete! Imported {count} GPs")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python import_gps_simple.py <path_to_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]

    # Backup existing database
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + ".backup"
        shutil.copy(DB_PATH, backup_path)
        print(f"Backed up existing database to: {backup_path}")

    # Recreate database with new schema
    print("Creating new database schema...")
    create_db_and_tables()

    # Import data
    print(f"\nImporting from: {csv_path}\n")
    import_gps_simple(csv_path)
