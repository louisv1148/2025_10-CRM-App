"""
Import Distributors from Notion CSV with relationships
Handles Distributor-GP and Distributor-Person relationships
"""

import csv
import re
from database import (
    Distributor, GP, Person,
    DistributorPersonLink,
    get_session, engine
)
from sqlmodel import Session, select


def extract_names_from_notion_links(text):
    """Extract names from Notion link format"""
    if not text or text.strip() == '':
        return []
    # Pattern: "Name (https://...)"
    pattern = r'([^,(]+?)\s*\(https://www\.notion\.so/[^)]+\)'
    matches = re.findall(pattern, text)
    return [name.strip() for name in matches]


def import_distributors(csv_path: str):
    """Import Distributors with GP and Person relationships"""

    with Session(engine) as session:
        # Build lookup dictionaries
        print("Building lookups...")
        gps = {gp.name: gp.id for gp in session.exec(select(GP)).all()}
        people = {person.name: person.id for person in session.exec(select(Person)).all()}

        print(f"Found {len(gps)} GPs and {len(people)} People in database\n")

        distributor_count = 0
        gp_links = 0
        person_links = 0

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                dist_name = row.get('Name', '').strip()
                if not dist_name:
                    continue

                print(f"\nImporting Distributor: {dist_name}")

                # Create or get Distributor
                existing_dist = session.exec(
                    select(Distributor).where(Distributor.name == dist_name)
                ).first()

                if existing_dist:
                    distributor = existing_dist
                    print(f"  - Distributor already exists (ID: {distributor.id})")
                else:
                    distributor = Distributor(
                        name=dist_name,
                        headquarter=row.get('Headquarter', '').strip() or None,
                        mexico=row.get('Mex', '').strip() or None,
                        text=row.get('Text', '').strip() or None,
                    )
                    session.add(distributor)
                    session.flush()  # Get ID
                    distributor_count += 1
                    print(f"  - Created Distributor (ID: {distributor.id})")

                # Link GPs via Managers column
                # Note: GPs link to Distributors via GP.distributor_id, not a link table
                # We'll update the GP's distributor_id field
                gp_names = extract_names_from_notion_links(row.get('Managers', ''))
                for gp_name in gp_names:
                    if gp_name in gps:
                        gp_id = gps[gp_name]
                        gp = session.get(GP, gp_id)
                        if gp and gp.distributor_id != distributor.id:
                            gp.distributor_id = distributor.id
                            session.add(gp)
                            gp_links += 1
                            print(f"  - Linked GP: {gp_name}")

                # Link People via Distributor-Person link table
                person_names = list(set(extract_names_from_notion_links(row.get('🕴️ CRM People ', ''))))
                for person_name in person_names:
                    if person_name in people:
                        person_id = people[person_name]

                        # Check if link already exists
                        existing_link = session.exec(
                            select(DistributorPersonLink).where(
                                DistributorPersonLink.distributor_id == distributor.id,
                                DistributorPersonLink.person_id == person_id
                            )
                        ).first()

                        if not existing_link:
                            link = DistributorPersonLink(
                                distributor_id=distributor.id,
                                person_id=person_id
                            )
                            session.add(link)
                            person_links += 1
                            print(f"  - Linked Person: {person_name}")

        session.commit()
        print(f"\n" + "="*60)
        print(f"✓ Import complete!")
        print(f"  - Created {distributor_count} new Distributors")
        print(f"  - Created {gp_links} GP relationships")
        print(f"  - Created {person_links} Person relationships")
        print("="*60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python import_distributors.py <path_to_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]
    print("Importing Distributors with relationships...\n")
    import_distributors(csv_path)
