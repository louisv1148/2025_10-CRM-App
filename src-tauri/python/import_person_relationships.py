"""
Import Person-GP and Person-LP relationships from Notion CSV files
Parses Notion link format and creates relationships
"""

import csv
import re
from database import Person, GP, LP, GPPersonLink, LPPersonLink, get_session, engine
from sqlmodel import Session, select


def extract_names_from_notion_links(text):
    """Extract names from Notion link format"""
    if not text or text.strip() == '':
        return []
    # Pattern: "Name (https://...)"
    pattern = r'([^,(]+?)\s*\(https://www\.notion\.so/[^)]+\)'
    matches = re.findall(pattern, text)
    return [name.strip() for name in matches]


def import_gp_person_relationships(csv_path: str):
    """Import GP-Person relationships from People CSV"""

    with Session(engine) as session:
        # Build lookup dictionaries
        print("Building GP lookup...")
        gps = {gp.name: gp.id for gp in session.exec(select(GP)).all()}

        print("Building Person lookup...")
        people = {person.name: person.id for person in session.exec(select(Person)).all()}

        print(f"\nFound {len(gps)} GPs and {len(people)} People in database\n")

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            links_created = 0
            for row in reader:
                person_name = row.get('Name', '').strip()
                if not person_name or person_name not in people:
                    continue

                person_id = people[person_name]

                # Parse GP links
                gp_names = extract_names_from_notion_links(row.get('🌆 CRM GPs', ''))

                for gp_name in gp_names:
                    if gp_name in gps:
                        gp_id = gps[gp_name]

                        # Check if link already exists
                        existing = session.exec(
                            select(GPPersonLink).where(
                                GPPersonLink.gp_id == gp_id,
                                GPPersonLink.person_id == person_id
                            )
                        ).first()

                        if not existing:
                            link = GPPersonLink(gp_id=gp_id, person_id=person_id)
                            session.add(link)
                            links_created += 1
                            print(f"✓ Linked {person_name} → {gp_name}")

        session.commit()
        print(f"\n✓ Created {links_created} GP-Person relationships")


def import_lp_person_relationships(csv_path: str):
    """Import LP-Person relationships from People CSV"""

    with Session(engine) as session:
        # Build lookup dictionaries
        print("Building LP lookup...")
        lps = {lp.name: lp.id for lp in session.exec(select(LP)).all()}

        print("Building Person lookup...")
        people = {person.name: person.id for person in session.exec(select(Person)).all()}

        print(f"\nFound {len(lps)} LPs and {len(people)} People in database\n")

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            links_created = 0
            for row in reader:
                person_name = row.get('Name', '').strip()
                if not person_name or person_name not in people:
                    continue

                person_id = people[person_name]

                # Parse LP links
                lp_names = extract_names_from_notion_links(row.get('💰 CRM LPs', ''))

                for lp_name in lp_names:
                    if lp_name in lps:
                        lp_id = lps[lp_name]

                        # Check if link already exists
                        existing = session.exec(
                            select(LPPersonLink).where(
                                LPPersonLink.lp_id == lp_id,
                                LPPersonLink.person_id == person_id
                            )
                        ).first()

                        if not existing:
                            link = LPPersonLink(lp_id=lp_id, person_id=person_id)
                            session.add(link)
                            links_created += 1
                            print(f"✓ Linked {person_name} → {lp_name}")

        session.commit()
        print(f"\n✓ Created {links_created} LP-Person relationships")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python import_person_relationships.py <path_to_people_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]

    print("=" * 60)
    print("IMPORTING GP-PERSON RELATIONSHIPS")
    print("=" * 60)
    import_gp_person_relationships(csv_path)

    print("\n" + "=" * 60)
    print("IMPORTING LP-PERSON RELATIONSHIPS")
    print("=" * 60)
    import_lp_person_relationships(csv_path)

    print("\n✓ All relationships imported successfully!")
