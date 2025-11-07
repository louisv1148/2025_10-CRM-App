#!/usr/bin/env python3
"""
Export Notion databases with their pages and subpages using the Notion API.
"""

import os
import json
import requests
from typing import Dict, List, Any
from datetime import datetime


class NotionExporter:
    """Export Notion databases and pages via API"""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"

    def query_database(self, database_id: str) -> List[Dict[str, Any]]:
        """Query all pages in a database"""
        url = f"{self.base_url}/databases/{database_id}/query"

        all_results = []
        has_more = True
        start_cursor = None

        while has_more:
            payload = {}
            if start_cursor:
                payload["start_cursor"] = start_cursor

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            all_results.extend(data.get("results", []))

            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")

        return all_results

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get a specific page"""
        url = f"{self.base_url}/pages/{page_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_page_blocks(self, page_id: str) -> List[Dict[str, Any]]:
        """Get all blocks (content) from a page"""
        url = f"{self.base_url}/blocks/{page_id}/children"

        all_blocks = []
        has_more = True
        start_cursor = None

        while has_more:
            params = {}
            if start_cursor:
                params["start_cursor"] = start_cursor

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            all_blocks.extend(data.get("results", []))

            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")

        return all_blocks

    def get_block_children_recursive(self, block_id: str) -> List[Dict[str, Any]]:
        """Recursively get all child blocks"""
        blocks = self.get_page_blocks(block_id)

        for block in blocks:
            if block.get("has_children"):
                block["children"] = self.get_block_children_recursive(block["id"])

        return blocks

    def export_database_with_pages(self, database_id: str, output_file: str):
        """Export database with all pages and their content"""
        print(f"Querying database {database_id}...")
        pages = self.query_database(database_id)
        print(f"Found {len(pages)} pages")

        export_data = {
            "database_id": database_id,
            "export_date": datetime.now().isoformat(),
            "pages": []
        }

        for i, page in enumerate(pages, 1):
            page_id = page["id"]
            print(f"Processing page {i}/{len(pages)}: {page_id}")

            # Get page properties
            page_data = {
                "id": page_id,
                "properties": page.get("properties", {}),
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time"),
            }

            # Get page content (blocks)
            try:
                blocks = self.get_block_children_recursive(page_id)
                page_data["blocks"] = blocks
            except Exception as e:
                print(f"  Warning: Could not get blocks for page {page_id}: {e}")
                page_data["blocks"] = []

            export_data["pages"].append(page_data)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\nExport complete: {output_file}")
        return export_data

    def extract_text_from_rich_text(self, rich_text_array: List[Dict]) -> str:
        """Extract plain text from Notion rich text array"""
        if not rich_text_array:
            return ""
        return "".join([rt.get("plain_text", "") for rt in rich_text_array])

    def extract_property_value(self, prop: Dict[str, Any]) -> Any:
        """Extract value from a Notion property"""
        prop_type = prop.get("type")

        if prop_type == "title":
            return self.extract_text_from_rich_text(prop.get("title", []))
        elif prop_type == "rich_text":
            return self.extract_text_from_rich_text(prop.get("rich_text", []))
        elif prop_type == "number":
            return prop.get("number")
        elif prop_type == "select":
            select = prop.get("select")
            return select.get("name") if select else None
        elif prop_type == "multi_select":
            return [ms.get("name") for ms in prop.get("multi_select", [])]
        elif prop_type == "date":
            date = prop.get("date")
            return date.get("start") if date else None
        elif prop_type == "checkbox":
            return prop.get("checkbox")
        elif prop_type == "url":
            return prop.get("url")
        elif prop_type == "email":
            return prop.get("email")
        elif prop_type == "phone_number":
            return prop.get("phone_number")
        elif prop_type == "relation":
            return [rel.get("id") for rel in prop.get("relation", [])]
        elif prop_type == "people":
            return [p.get("id") for p in prop.get("people", [])]
        else:
            return None


def main():
    """Main function to run exports"""
    import sys

    # Get API token from environment variable
    api_token = os.getenv("NOTION_API_TOKEN")

    if not api_token:
        print("ERROR: NOTION_API_TOKEN environment variable not set")
        print("\nTo set up:")
        print("1. Go to https://www.notion.so/my-integrations")
        print("2. Create a new integration")
        print("3. Copy the Internal Integration Token")
        print("4. Set environment variable: export NOTION_API_TOKEN='your_token_here'")
        print("5. Share your database with the integration")
        return

    exporter = NotionExporter(api_token)

    # Get database ID from command line or prompt
    if len(sys.argv) > 1:
        database_id = sys.argv[1].strip()
    else:
        database_id = input("Enter Notion Database ID: ").strip()

    output_file = f"notion_export_{database_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        exporter.export_database_with_pages(database_id, output_file)
    except requests.exceptions.HTTPError as e:
        print(f"\nERROR: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') else 'No response'}")
        print("\nMake sure:")
        print("1. Your API token is valid")
        print("2. The database is shared with your integration")
        print("3. The database ID is correct")


if __name__ == "__main__":
    main()
