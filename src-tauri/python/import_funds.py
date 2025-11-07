#!/usr/bin/env python3
"""
Import Funds from Notion export JSON
"""

import json
from datetime import datetime
from database import Fund, get_session
from sqlmodel import select


def parse_notion_date(date_obj):
    """Parse Notion date object"""
    if not date_obj or not isinstance(date_obj, dict):
        return None

    start = date_obj.get('start')
    if not start:
        return None

    try:
        return datetime.fromisoformat(start.replace('Z', '+00:00'))
    except:
        return None


def parse_notion_property(prop):
    """Extract value from Notion property"""
    if not prop:
        return None

    prop_type = prop.get('type')

    if prop_type == 'title':
        texts = prop.get('title', [])
        return ''.join([t.get('plain_text', '') for t in texts]) if texts else None
    elif prop_type == 'rich_text':
        texts = prop.get('rich_text', [])
        return ''.join([t.get('plain_text', '') for t in texts]) if texts else None
    elif prop_type == 'number':
        return prop.get('number')
    elif prop_type == 'select':
        sel = prop.get('select')
        return sel.get('name') if sel else None
    elif prop_type == 'multi_select':
        items = prop.get('multi_select', [])
        return ', '.join([item.get('name', '') for item in items]) if items else None
    elif prop_type == 'date':
        return parse_notion_date(prop.get('date'))
    elif prop_type == 'checkbox':
        return prop.get('checkbox', False)
    elif prop_type == 'relation':
        # For GP relation, we'll store the first notion_id
        relations = prop.get('relation', [])
        return relations[0].get('id') if relations else None

    return None


def import_funds(json_file_path):
    """Import funds from Notion export JSON"""
    print(f"Loading funds from {json_file_path}")

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    pages = data.get('pages', [])
    print(f"Found {len(pages)} funds to import")

    with get_session() as session:
        imported = 0
        updated = 0
        skipped = 0

        for page in pages:
            notion_id = page.get('id')
            props = page.get('properties', {})

            # Extract all properties
            fund_name = parse_notion_property(props.get('Fund Name'))
            if not fund_name:
                print(f"Skipping fund with no name (notion_id: {notion_id})")
                skipped += 1
                continue

            # Check if fund already exists
            existing = session.exec(
                select(Fund).where(Fund.notion_id == notion_id)
            ).first()

            fund_data = {
                'notion_id': notion_id,
                'fund_name': fund_name,
                'geography': parse_notion_property(props.get('Geography')),
                'target_multiple': parse_notion_property(props.get('Target Multiple')),
                'status': parse_notion_property(props.get('Status')),
                'days_to_rs': parse_notion_property(props.get('Days to RS')),
                'target_irr': parse_notion_property(props.get('Target IRR')),
                'hard_cap_mn': parse_notion_property(props.get('Hard Cap mn')),
                'target_mn': parse_notion_property(props.get('Target mn')),
                'roadshow_date': parse_notion_property(props.get('Roadshow Date')),
                'sectors': parse_notion_property(props.get('Sectors')),
                'note': parse_notion_property(props.get('Note')),
                'potential': parse_notion_property(props.get('Potential')),
                'asset_class': parse_notion_property(props.get('Asset Class')),
                'current_lps': parse_notion_property(props.get('Current LPs')),
                'launch': parse_notion_property(props.get('Launch')),
                'roadshows': parse_notion_property(props.get('Roadshows')),
                'final_close': parse_notion_property(props.get('Final Close')),
                'closed': parse_notion_property(props.get('Closed')),
                'gp_notion_id': parse_notion_property(props.get('GP'))
            }

            if existing:
                # Update existing fund
                for key, value in fund_data.items():
                    if key != 'notion_id':  # Don't update notion_id
                        setattr(existing, key, value)
                updated += 1
                print(f"Updated: {fund_name}")
            else:
                # Create new fund
                fund = Fund(**fund_data)
                session.add(fund)
                imported += 1
                print(f"Imported: {fund_name}")

        session.commit()

        print(f"\nImport complete!")
        print(f"  Imported: {imported}")
        print(f"  Updated: {updated}")
        print(f"  Skipped: {skipped}")
        print(f"  Total: {imported + updated}")


if __name__ == "__main__":
    import_funds("../../notion_export_35abba89d7114f0293d78ad81b8f2081_20251106_105814.json")
