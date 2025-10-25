"""
Import Notion CRM data from CSV export
Handles GP data with all relationships
"""

import csv
import re
import os
import shutil
from database import (
    GP, LP, Person, Distributor, Note,
    GPLPLink, GPPersonLink,
    create_db_and_tables, get_session, engine
)
from sqlmodel import Session, select

def extract_names_from_notion_links(text):
    """
    Extract names from Notion link format:
    'Name (https://www.notion.so/...), Name2 (https://...)'
    Returns list of names
    """
    if not text or text.strip() == '':
        return []

    # Pattern to match: "Name (https://...)"
    pattern = r'([^,(]+?)\s*\(https://www\.notion\.so/[^)]+\)'
    matches = re.findall(pattern, text)
    return [name.strip() for name in matches]


def import_gps_from_csv(csv_path: str):
    """Import GP data from Notion CSV export"""

    with Session(engine) as session:
        # Track entities for relationships
        distributors_cache = {}
        lps_cache = {}
        people_cache = {}

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                gp_name = row['Name'].strip()
                if not gp_name:
                    continue

                print(f"\nProcessing GP: {gp_name}")

                # Create or get distributor
                distributor_id = None
                distributor_names = extract_names_from_notion_links(row.get('👞 CRM Distributor', ''))
                if distributor_names:
                    dist_name = distributor_names[0]  # Take first distributor
                    if dist_name not in distributors_cache:
                        dist = session.exec(select(Distributor).where(Distributor.name == dist_name)).first()
                        if not dist:
                            dist = Distributor(name=dist_name)
                            session.add(dist)
                            session.flush()
                        distributors_cache[dist_name] = dist.id
                    distributor_id = distributors_cache[dist_name]

                # Create GP
                gp = GP(
                    name=gp_name,
                    location=row.get('Location', '').strip() or None,
                    contact_level=row.get('Contact Level', '').strip() or None,
                    flagship_strategy=row.get('Flagship', '').strip() or None,
                    other_strategies=row.get('Others', '').strip() or None,
                    note=row.get('Note', '').strip() or None,
                    distributor_id=distributor_id
                )
                session.add(gp)
                session.flush()  # Get GP ID

                print(f"  - Created GP with ID: {gp.id}")

                # Link LPs
                lp_names = extract_names_from_notion_links(row.get('💰 CRM LPs', ''))
                for lp_name in lp_names:
                    if lp_name not in lps_cache:
                        lp = session.exec(select(LP).where(LP.name == lp_name)).first()
                        if not lp:
                            lp = LP(name=lp_name)
                            session.add(lp)
                            session.flush()
                        lps_cache[lp_name] = lp.id

                    # Create link
                    link = GPLPLink(gp_id=gp.id, lp_id=lps_cache[lp_name])
                    session.add(link)
                    print(f"  - Linked to LP: {lp_name}")

                # Link People (deduplicate first)
                people_names = list(set(extract_names_from_notion_links(row.get('🕴️ CRM People ', ''))))
                for person_name in people_names:
                    if person_name not in people_cache:
                        person = session.exec(select(Person).where(Person.name == person_name)).first()
                        if not person:
                            person = Person(
                                name=person_name,
                                role="",  # Not in CSV
                                org_type="GP",
                                org_id=gp.id
                            )
                            session.add(person)
                            session.flush()
                        people_cache[person_name] = person.id

                    # Create link (check if it already exists)
                    existing_link = session.exec(
                        select(GPPersonLink).where(
                            GPPersonLink.gp_id == gp.id,
                            GPPersonLink.person_id == people_cache[person_name]
                        )
                    ).first()
                    if not existing_link:
                        link = GPPersonLink(gp_id=gp.id, person_id=people_cache[person_name])
                        session.add(link)
                        print(f"  - Linked to Person: {person_name}")

        session.commit()
        print("\n✓ Import complete!")


if __name__ == "__main__":
    import sys
    from database import DB_PATH

    if len(sys.argv) < 2:
        print("Usage: python import_notion_data.py <path_to_csv>")
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
    print(f"\nImporting from: {csv_path}")
    import_gps_from_csv(csv_path)
