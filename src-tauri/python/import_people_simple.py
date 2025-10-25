"""
Simple People/Contacts import from Notion CSV - Core fields only
Skips relational data (GP, LP links) for now
"""

import csv
import os
from database import Person, create_db_and_tables, get_session, engine
from sqlmodel import Session

def import_people_simple(csv_path: str):
    """Import People data from Notion CSV - core fields only"""

    with Session(engine) as session:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                person_name = row.get('Name', '').strip()
                if not person_name:
                    continue

                print(f"Importing Person: {person_name}")

                # Create Person with core fields
                person = Person(
                    name=person_name,
                    cell_phone=row.get('Cell', '').strip() or None,
                    office_phone=row.get('Office', '').strip() or None,
                    email=row.get('Email', '').strip() or None,
                    location=row.get('Location', '').strip() or None,
                    position=row.get('Position', '').strip() or None,
                    people_type=row.get('People Type', '').strip() or None,
                    personal_note=row.get('Personal', '').strip() or None,
                )
                session.add(person)
                count += 1

        session.commit()
        print(f"\n✓ Import complete! Imported {count} People")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python import_people_simple.py <path_to_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]

    # Ensure tables exist (won't overwrite existing data)
    create_db_and_tables()

    print(f"Importing People from: {csv_path}\n")
    import_people_simple(csv_path)
