#!/usr/bin/env python3
"""
Complete Notion CRM import script.
Migrates schema, clears old data, and imports all entities with relationships.
"""

import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "../../db/crm.db")


def migrate_schema():
    """Add notion_id columns and create link tables"""
    print("=" * 80)
    print("MIGRATING DATABASE SCHEMA")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add notion_id columns to existing tables
    tables_to_migrate = ['gp', 'lp', 'distributor', 'person', 'note']

    for table in tables_to_migrate:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row[1] for row in cursor.fetchall()}

        if 'notion_id' not in columns:
            print(f"  Adding notion_id to {table}")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN notion_id VARCHAR")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_notion_id ON {table}(notion_id)")

    # Add Note fields
    cursor.execute("PRAGMA table_info(note)")
    note_columns = {row[1] for row in cursor.fetchall()}

    note_fields = [
        ('name', 'VARCHAR'),
        ('contact_type', 'VARCHAR'),
        ('local_mf', 'VARCHAR'),
        ('local_alts', 'VARCHAR'),
        ('intl_mf', 'VARCHAR'),
        ('intl_alts', 'VARCHAR'),
        ('roadshows', 'VARCHAR'),
        ('pin', 'VARCHAR'),
        ('useful', 'INTEGER'),
        ('ai_summary', 'VARCHAR'),
        ('content_text', 'VARCHAR'),
        ('content_json', 'VARCHAR'),
        ('image_paths', 'VARCHAR'),
    ]

    for field_name, field_type in note_fields:
        if field_name not in note_columns:
            print(f"  Adding {field_name} to note")
            cursor.execute(f"ALTER TABLE note ADD COLUMN {field_name} {field_type}")

    # Create link tables
    link_tables = [
        ('notegplink', 'note_id', 'gp_id'),
        ('notelplink', 'note_id', 'lp_id'),
        ('notedistributorlink', 'note_id', 'distributor_id'),
    ]

    for table_name, fk1, fk2 in link_tables:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {fk1} INTEGER NOT NULL,
                {fk2} INTEGER NOT NULL,
                PRIMARY KEY ({fk1}, {fk2})
            )
        """)
        print(f"  Created {table_name} table (if not exists)")

    conn.commit()
    conn.close()
    print("\n✓ Schema migration complete\n")


def clear_old_data():
    """Clear all existing data for fresh import"""
    print("=" * 80)
    print("CLEARING OLD DATA")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear in order (respecting foreign keys)
    tables = [
        'todo', 'notegplink', 'notelplink', 'notedistributorlink',
        'gplink', 'gppersonlink', 'lppersonlink', 'distributorpersonlink',
        'note', 'person', 'gp', 'lp', 'distributor'
    ]

    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  Cleared {table}")
        except sqlite3.OperationalError:
            pass  # Table might not exist

    conn.commit()
    conn.close()
    print("\n✓ Old data cleared\n")


def extract_text_from_rich_text(rich_text_array):
    """Extract plain text from Notion rich text"""
    if not rich_text_array:
        return ""
    return "".join([rt.get("plain_text", "") for rt in rich_text_array])


def extract_property_value(prop, for_storage=True):
    """Extract value from Notion property

    Args:
        prop: The Notion property object
        for_storage: If True, convert lists to strings for database storage.
                     If False, keep lists (for relation processing)
    """
    prop_type = prop.get("type")

    if prop_type == "title":
        return extract_text_from_rich_text(prop.get("title", []))
    elif prop_type == "rich_text":
        return extract_text_from_rich_text(prop.get("rich_text", []))
    elif prop_type == "number":
        return prop.get("number")
    elif prop_type == "select":
        select = prop.get("select")
        return select.get("name") if select else None
    elif prop_type == "multi_select":
        # Convert multi_select to comma-separated string
        values = [ms.get("name") for ms in prop.get("multi_select", [])]
        return ", ".join(values) if values else None
    elif prop_type == "date":
        date = prop.get("date")
        return date.get("start") if date else None
    elif prop_type == "checkbox":
        return prop.get("checkbox")
    elif prop_type == "email":
        return prop.get("email")
    elif prop_type == "phone_number":
        return prop.get("phone_number")
    elif prop_type == "relation":
        # Relations: return list if not for storage, else return None (we handle these separately)
        relation_list = [rel.get("id") for rel in prop.get("relation", [])]
        if for_storage:
            return None  # Relations are stored in link tables, not as text
        else:
            return relation_list
    elif prop_type == "rollup":
        # Rollups can contain various types - try to extract the value
        rollup = prop.get("rollup", {})
        rollup_type = rollup.get("type")
        if rollup_type == "number":
            return rollup.get("number")
        elif rollup_type == "array":
            # Array rollups - convert to comma-separated string if for storage
            values = []
            for item in rollup.get("array", []):
                if item.get("type") == "select":
                    select = item.get("select")
                    if select:
                        values.append(select.get("name"))
            return ", ".join(values) if values and for_storage else (values if values else None)
        else:
            return None
    else:
        return None


def import_distributors(export_file):
    """Import distributors from Notion export"""
    print("Importing Distributors...")

    with open(export_file, 'r') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for page in data['pages']:
        notion_id = page['id']
        props = page.get('properties', {})

        name = extract_property_value(props.get('Name', {}))
        headquarter = extract_property_value(props.get('Headquarter', {}))
        mexico = extract_property_value(props.get('Mex', {}))
        text = extract_property_value(props.get('Text', {}))

        cursor.execute("""
            INSERT INTO distributor (notion_id, name, headquarter, mexico, text)
            VALUES (?, ?, ?, ?, ?)
        """, (notion_id, name, headquarter, mexico, text))

    conn.commit()
    conn.close()
    print(f"  ✓ Imported {len(data['pages'])} distributors\n")


def import_lps(export_file):
    """Import LPs from Notion export"""
    print("Importing LPs...")

    with open(export_file, 'r') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for page in data['pages']:
        notion_id = page['id']
        props = page.get('properties', {})

        name = extract_property_value(props.get('Name', {}))
        aum = extract_property_value(props.get('AUM (B)', {}))

        # Advisor is a relation - store as comma-separated IDs for now
        advisor_relations = props.get('Advisor', {}).get('relation', [])
        advisor = ', '.join([rel['id'] for rel in advisor_relations]) if advisor_relations else None

        # Fix field name typo: "Intl. Atls." in Notion (not "Alts")
        intl_alts = extract_property_value(props.get('Intl. Atls.', {}))
        intl_mf = extract_property_value(props.get('Intl. MF', {}))
        local_alts = extract_property_value(props.get('Local Alts.', {}))
        local_mf = extract_property_value(props.get('Local MF', {}))

        # Investment HIGH and LOW are separate number fields
        inv_low = extract_property_value(props.get('Investment LOW', {}))
        inv_high = extract_property_value(props.get('Investment HIGH', {}))

        location = extract_property_value(props.get('Location', {}))
        priority = extract_property_value(props.get('Priority', {}))
        type_of_group = extract_property_value(props.get('Type of Group', {}))
        text = extract_property_value(props.get('Text', {}))

        cursor.execute("""
            INSERT INTO lp (notion_id, name, aum_billions, advisor, intl_alts, intl_mf,
                           local_alts, local_mf, investment_high, investment_low, location,
                           priority, type_of_group, text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (notion_id, name, aum, advisor, intl_alts, intl_mf, local_alts, local_mf,
              inv_high, inv_low, location, priority, type_of_group, text))

    conn.commit()
    conn.close()
    print(f"  ✓ Imported {len(data['pages'])} LPs\n")


def import_gps(export_file):
    """Import GPs from Notion export"""
    print("Importing GPs...")

    with open(export_file, 'r') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Build distributor lookup by notion_id
    cursor.execute("SELECT id, notion_id FROM distributor")
    dist_lookup = {notion_id: id for id, notion_id in cursor.fetchall()}

    for page in data['pages']:
        notion_id = page['id']
        props = page.get('properties', {})

        name = extract_property_value(props.get('Name', {}))
        location = extract_property_value(props.get('Location', {}))
        contact_level = extract_property_value(props.get('Contact Level', {}))
        flagship = extract_property_value(props.get('Flagship', {}))
        others = extract_property_value(props.get('Others', {}))
        note = extract_property_value(props.get('Note', {}))

        # Get distributor relation
        distributor_relations = extract_property_value(props.get('👞 CRM Distributor', {}), for_storage=False)
        distributor_id = None
        if distributor_relations and len(distributor_relations) > 0:
            dist_notion_id = distributor_relations[0]
            distributor_id = dist_lookup.get(dist_notion_id)

        cursor.execute("""
            INSERT INTO gp (notion_id, name, location, contact_level, flagship_strategy,
                           other_strategies, note, distributor_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (notion_id, name, location, contact_level, flagship, others, note, distributor_id))

    conn.commit()
    conn.close()
    print(f"  ✓ Imported {len(data['pages'])} GPs\n")


def import_people(export_file):
    """Import People from Notion export with LP/GP/Distributor relationships"""
    print("Importing People...")

    with open(export_file, 'r') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Build lookups for relationships
    cursor.execute("SELECT id, notion_id FROM lp")
    lp_lookup = {notion_id: id for id, notion_id in cursor.fetchall()}

    cursor.execute("SELECT id, notion_id FROM gp")
    gp_lookup = {notion_id: id for id, notion_id in cursor.fetchall()}

    cursor.execute("SELECT id, notion_id FROM distributor")
    dist_lookup = {notion_id: id for id, notion_id in cursor.fetchall()}

    lp_person_links = []
    gp_person_links = []
    dist_person_links = []

    for page in data['pages']:
        notion_id = page['id']
        props = page.get('properties', {})

        name = extract_property_value(props.get('Name', {}))
        cell = extract_property_value(props.get('Cell', {}))
        office = extract_property_value(props.get('Office', {}))
        email = extract_property_value(props.get('Email', {}))
        location = extract_property_value(props.get('Location', {}))
        people_type = extract_property_value(props.get('People Type', {}))
        position = extract_property_value(props.get('Position', {}))
        personal = extract_property_value(props.get('Personal', {}))

        cursor.execute("""
            INSERT INTO person (notion_id, name, cell_phone, office_phone, email,
                              location, people_type, position, personal_note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (notion_id, name, cell, office, email, location, people_type, position, personal))

        person_id = cursor.lastrowid

        # Extract LP relationships (💰 CRM LPs)
        lp_relations = props.get('💰 CRM LPs', {}).get('relation', [])
        for rel in lp_relations:
            lp_notion_id = rel['id']
            if lp_notion_id in lp_lookup:
                lp_person_links.append((lp_lookup[lp_notion_id], person_id))

        # Extract GP relationships (🌆 CRM GPs)
        gp_relations = props.get('🌆 CRM GPs', {}).get('relation', [])
        for rel in gp_relations:
            gp_notion_id = rel['id']
            if gp_notion_id in gp_lookup:
                gp_person_links.append((gp_lookup[gp_notion_id], person_id))

        # Extract Distributor relationships (👞 CRM Distributor)
        dist_relations = props.get('👞 CRM Distributor', {}).get('relation', [])
        for rel in dist_relations:
            dist_notion_id = rel['id']
            if dist_notion_id in dist_lookup:
                dist_person_links.append((dist_lookup[dist_notion_id], person_id))

    # Insert all relationship links
    if lp_person_links:
        cursor.executemany("INSERT OR IGNORE INTO lppersonlink (lp_id, person_id) VALUES (?, ?)", lp_person_links)

    if gp_person_links:
        cursor.executemany("INSERT OR IGNORE INTO gppersonlink (gp_id, person_id) VALUES (?, ?)", gp_person_links)

    if dist_person_links:
        cursor.executemany("INSERT OR IGNORE INTO distributorpersonlink (distributor_id, person_id) VALUES (?, ?)", dist_person_links)

    conn.commit()
    conn.close()
    print(f"  ✓ Imported {len(data['pages'])} people")
    print(f"  ✓ Created {len(lp_person_links)} LP-Person relationships")
    print(f"  ✓ Created {len(gp_person_links)} GP-Person relationships")
    print(f"  ✓ Created {len(dist_person_links)} Distributor-Person relationships\n")


def import_notes(export_file):
    """Import Notes from Notion export with all relationships"""
    print("Importing Notes (this may take a while)...")

    with open(export_file, 'r') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Build lookups
    cursor.execute("SELECT id, notion_id FROM gp")
    gp_lookup = {notion_id: id for id, notion_id in cursor.fetchall()}

    cursor.execute("SELECT id, notion_id FROM lp")
    lp_lookup = {notion_id: id for id, notion_id in cursor.fetchall()}

    cursor.execute("SELECT id, notion_id FROM distributor")
    dist_lookup = {notion_id: id for id, notion_id in cursor.fetchall()}

    imported_count = 0
    gp_links = 0
    lp_links = 0
    dist_links = 0

    for i, page in enumerate(data['pages'], 1):
        if i % 100 == 0:
            print(f"  Processing note {i}/{len(data['pages'])}...")

        notion_id = page['id']
        props = page.get('properties', {})

        name = extract_property_value(props.get('Name', {}))
        date_str = extract_property_value(props.get('Date', {}))
        contact_type = extract_property_value(props.get('Contact Type', {}))
        local_mf = extract_property_value(props.get('Local MF', {}))
        local_alts = extract_property_value(props.get('Local Alts.', {}))
        intl_mf = extract_property_value(props.get('Intl. MF', {}))
        intl_alts = extract_property_value(props.get('Intl. Alts', {}))
        roadshows = extract_property_value(props.get('Roadshows', {}))
        pin = extract_property_value(props.get('PIN', {}))
        useful = extract_property_value(props.get('Useful', {}))
        fundraise = extract_property_value(props.get('Fundraise', {}))
        ai_summary = extract_property_value(props.get('AI summary', {}))

        # Extract blocks content
        blocks = page.get('blocks', [])
        content_json = json.dumps(blocks) if blocks else None

        # Extract image paths
        image_paths = []
        for block in blocks:
            if block.get('type') == 'image' and block.get('local_image_path'):
                image_paths.append(block['local_image_path'])
        image_paths_str = ','.join(image_paths) if image_paths else None

        # Parse date (use page created_time as fallback if no date)
        note_date = None
        if date_str:
            try:
                note_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass

        # If still no date, use created_time from page or January 1, 1900
        if not note_date:
            created_time = page.get('created_time')
            if created_time:
                try:
                    note_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                except:
                    note_date = datetime(1900, 1, 1)
            else:
                note_date = datetime(1900, 1, 1)

        # Insert note (including legacy fields for compatibility)
        cursor.execute("""
            INSERT INTO note (notion_id, name, date, contact_type, local_mf, local_alts,
                            intl_mf, intl_alts, roadshows, pin, useful, fundraise,
                            ai_summary, content_json, image_paths, raw_notes, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (notion_id, name, note_date, contact_type, local_mf, local_alts, intl_mf,
              intl_alts, roadshows, pin, useful, fundraise, ai_summary, content_json,
              image_paths_str, content_json or '', ai_summary or ''))

        note_id = cursor.lastrowid
        imported_count += 1

        # Create GP relationships
        gp_relations = extract_property_value(props.get('CRM GPs', {}), for_storage=False)
        if gp_relations:
            for gp_notion_id in gp_relations:
                if gp_notion_id in gp_lookup:
                    cursor.execute("""
                        INSERT INTO notegplink (note_id, gp_id) VALUES (?, ?)
                    """, (note_id, gp_lookup[gp_notion_id]))
                    gp_links += 1

        # Create LP relationships
        lp_relations = extract_property_value(props.get('CRM LPs', {}), for_storage=False)
        if lp_relations:
            for lp_notion_id in lp_relations:
                if lp_notion_id in lp_lookup:
                    cursor.execute("""
                        INSERT INTO notelplink (note_id, lp_id) VALUES (?, ?)
                    """, (note_id, lp_lookup[lp_notion_id]))
                    lp_links += 1

        # Create Distributor relationships
        dist_relations = extract_property_value(props.get('CRM Distributors', {}), for_storage=False)
        if dist_relations:
            for dist_notion_id in dist_relations:
                if dist_notion_id in dist_lookup:
                    cursor.execute("""
                        INSERT INTO notedistributorlink (note_id, distributor_id) VALUES (?, ?)
                    """, (note_id, dist_lookup[dist_notion_id]))
                    dist_links += 1

    conn.commit()
    conn.close()

    print(f"  ✓ Imported {imported_count} notes")
    print(f"  ✓ Created {gp_links} Note-GP relationships")
    print(f"  ✓ Created {lp_links} Note-LP relationships")
    print(f"  ✓ Created {dist_links} Note-Distributor relationships\n")


def main():
    """Main import workflow"""
    print("\n" + "=" * 80)
    print("NOTION CRM COMPLETE IMPORT")
    print("=" * 80 + "\n")

    # Migrate schema
    migrate_schema()

    # Clear old data
    clear_old_data()

    # Import in order (respecting dependencies)
    print("=" * 80)
    print("IMPORTING DATA FROM NOTION EXPORTS")
    print("=" * 80 + "\n")

    import_distributors('notion_export_ced0e422594344019215685a01968341_20251104_175542.json')
    import_lps('notion_export_f8e8e49595504e24843093a86170ba4e_20251104_175547.json')
    import_gps('notion_export_3a440409b8f249319081379ff5b10e89_20251104_175602.json')
    import_people('notion_export_79e695dba97e415b87d2dc1d5eb67cd2_20251104_175605.json')
    import_notes('notion_export_with_images_6b3d8f29d43d402c86a530758b340a72_20251103_215037.json')

    print("=" * 80)
    print("✓ IMPORT COMPLETE!")
    print("=" * 80)
    print("\nYour CRM database is now fully populated from Notion with all relationships intact!")


if __name__ == "__main__":
    main()
