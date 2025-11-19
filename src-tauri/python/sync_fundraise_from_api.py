#!/usr/bin/env python3
"""
Sync Fundraise relationships from Notion API to database.
This script fetches the current Fundraise property values from Notion and updates the database.
"""

import os
import sqlite3
import requests
from typing import Dict, List

# Notion API credentials
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_NOTES_DATABASE_ID")  # Your Notes database ID

DB_PATH = os.path.join(os.path.dirname(__file__), "../../db/crm.db")

def get_notion_headers():
    """Get headers for Notion API requests"""
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

def fetch_all_notes_from_notion() -> List[Dict]:
    """Fetch all notes from Notion database with their Fundraise property"""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = get_notion_headers()

    all_results = []
    has_more = True
    start_cursor = None

    print("Fetching notes from Notion API...")

    while has_more:
        payload = {}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Error fetching from Notion API: {response.status_code}")
            print(response.text)
            return []

        data = response.json()
        all_results.extend(data.get("results", []))

        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

        print(f"  Fetched {len(all_results)} notes so far...")

    print(f"✓ Fetched {len(all_results)} notes total from Notion API\n")
    return all_results

def sync_fundraise_relationships():
    """Sync Fundraise relationships from Notion API to database"""

    # Check for API credentials
    if not NOTION_API_KEY:
        print("ERROR: NOTION_API_KEY environment variable not set")
        print("Please set it with: export NOTION_API_KEY='your-api-key'")
        return

    if not NOTION_DATABASE_ID:
        print("ERROR: NOTION_NOTES_DATABASE_ID environment variable not set")
        print("Please set it with: export NOTION_NOTES_DATABASE_ID='your-database-id'")
        return

    # Fetch notes from Notion API
    notion_notes = fetch_all_notes_from_notion()

    if not notion_notes:
        print("No notes fetched from Notion. Exiting.")
        return

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Build lookups
    print("Building database lookups...")
    cursor.execute("SELECT id, notion_id FROM note")
    note_lookup = {notion_id: db_id for db_id, notion_id in cursor.fetchall()}

    cursor.execute("SELECT id, notion_id FROM fund")
    fund_lookup = {notion_id: db_id for db_id, notion_id in cursor.fetchall()}

    print(f"  Found {len(note_lookup)} notes in database")
    print(f"  Found {len(fund_lookup)} funds in database\n")

    # Clear existing fundraise relationships
    print("Clearing existing Note-Fund relationships...")
    cursor.execute("DELETE FROM notefundlink")
    print(f"  Deleted all existing relationships\n")

    # Process each note
    print("Syncing Fundraise relationships...")
    created_links = 0
    notes_with_fundraise = 0
    skipped_notes = 0

    for notion_note in notion_notes:
        notion_id = notion_note["id"]

        # Check if note exists in our database
        if notion_id not in note_lookup:
            skipped_notes += 1
            continue

        db_note_id = note_lookup[notion_id]

        # Get Fundraise property
        properties = notion_note.get("properties", {})
        fundraise_prop = properties.get("Fundraise", {})
        fundraise_relations = fundraise_prop.get("relation", [])

        if fundraise_relations:
            notes_with_fundraise += 1

            # Create link for each related fund
            for fund_relation in fundraise_relations:
                fund_notion_id = fund_relation["id"]

                if fund_notion_id in fund_lookup:
                    db_fund_id = fund_lookup[fund_notion_id]

                    cursor.execute("""
                        INSERT INTO notefundlink (note_id, fund_id)
                        VALUES (?, ?)
                    """, (db_note_id, db_fund_id))

                    created_links += 1

    conn.commit()
    conn.close()

    print(f"\n{'='*80}")
    print(f"SYNC COMPLETE!")
    print(f"{'='*80}")
    print(f"  Total notes processed: {len(notion_notes)}")
    print(f"  Notes with Fundraise relations: {notes_with_fundraise}")
    print(f"  Notes skipped (not in DB): {skipped_notes}")
    print(f"  Total Note-Fund links created: {created_links}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    sync_fundraise_relationships()
