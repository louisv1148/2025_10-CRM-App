"""
Simple LP import from Notion CSV - Core fields only
"""

import csv
import os
import shutil
from database import LP, create_db_and_tables, get_session, engine, DB_PATH
from sqlmodel import Session

def parse_number(value: str) -> float:
    """Parse number from string, handling empty/None values"""
    if not value or value.strip() == '':
        return None
    try:
        # Remove commas and convert to float
        cleaned = value.replace(',', '').strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def import_lps_simple(csv_path: str):
    """Import LP data from Notion CSV - core fields only"""

    with Session(engine) as session:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                lp_name = row.get('Name', '').strip()
                if not lp_name:
                    continue

                print(f"Importing LP: {lp_name}")

                # Create LP with core fields
                lp = LP(
                    name=lp_name,
                    aum_billions=parse_number(row.get('AUM (B)', '')),
                    advisor=row.get('Advisor', '').strip() or None,
                    intl_alts=row.get('Intl. Atls. ', '').strip() or None,
                    intl_mf=row.get('Intl. MF', '').strip() or None,
                    local_alts=row.get('Local Alts.', '').strip() or None,
                    local_mf=row.get('Local MF', '').strip() or None,
                    investment_high=parse_number(row.get('Investment HIGH', '')),
                    investment_low=parse_number(row.get('Investment LOW', '')),
                    location=row.get('Location', '').strip() or None,
                    priority=row.get('Priority', '').strip() or None,
                    type_of_group=row.get('Type of Group', '').strip() or None,
                    text=row.get('Text', '').strip() or None,
                )
                session.add(lp)
                count += 1

        session.commit()
        print(f"\n✓ Import complete! Imported {count} LPs")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python import_lps_simple.py <path_to_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]

    # Note: We're UPDATING the existing database, not recreating it
    # The GP data should remain intact
    print(f"Importing LPs from: {csv_path}\n")

    # Ensure tables exist (won't overwrite existing data)
    create_db_and_tables()

    import_lps_simple(csv_path)
