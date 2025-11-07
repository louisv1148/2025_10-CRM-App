#!/usr/bin/env python3
"""
Export Notion databases with their pages, subpages, and download all images.
"""

import os
import json
import requests
from typing import Dict, List, Any
from datetime import datetime
import hashlib
from pathlib import Path


class NotionExporterWithImages:
    """Export Notion databases and pages via API, downloading images locally"""

    def __init__(self, api_token: str, image_dir: str = "notion_images"):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"
        self.image_dir = image_dir

        # Create image directory if it doesn't exist
        Path(image_dir).mkdir(exist_ok=True)

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

    def download_image(self, url: str, block_id: str) -> str:
        """Download an image and return the local file path"""
        try:
            # Create a hash of the URL to use as filename
            url_hash = hashlib.md5(url.encode()).hexdigest()

            # Get file extension from URL (before query params)
            ext = ".png"  # default
            if "?" in url:
                file_part = url.split("?")[0]
                if "." in file_part:
                    ext = "." + file_part.split(".")[-1]

            filename = f"{block_id}_{url_hash}{ext}"
            filepath = os.path.join(self.image_dir, filename)

            # Skip if already downloaded
            if os.path.exists(filepath):
                return filepath

            # Download the image
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"  ✓ Downloaded image: {filename}")
            return filepath

        except Exception as e:
            print(f"  ✗ Failed to download image: {e}")
            return None

    def process_image_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Process an image block and download the image"""
        if block.get("type") != "image":
            return block

        image_data = block.get("image", {})
        image_url = None

        if image_data.get("type") == "file":
            image_url = image_data["file"].get("url")
        elif image_data.get("type") == "external":
            image_url = image_data["external"].get("url")

        if image_url:
            local_path = self.download_image(image_url, block["id"])
            if local_path:
                # Add local path to the block data
                block["local_image_path"] = local_path

        return block

    def get_block_children_recursive(self, block_id: str) -> List[Dict[str, Any]]:
        """Recursively get all child blocks and download images"""
        blocks = self.get_page_blocks(block_id)

        processed_blocks = []
        for block in blocks:
            # Process images
            block = self.process_image_block(block)

            # Recursively process children
            if block.get("has_children"):
                block["children"] = self.get_block_children_recursive(block["id"])

            processed_blocks.append(block)

        return processed_blocks

    def export_database_with_pages(self, database_id: str, output_file: str):
        """Export database with all pages, content, and images"""
        print(f"Querying database {database_id}...")
        pages = self.query_database(database_id)
        print(f"Found {len(pages)} pages")

        export_data = {
            "database_id": database_id,
            "export_date": datetime.now().isoformat(),
            "pages": []
        }

        images_downloaded = 0

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

            # Get page content (blocks) and download images
            try:
                blocks = self.get_block_children_recursive(page_id)
                page_data["blocks"] = blocks

                # Count images in this page
                def count_images(blocks_list):
                    count = 0
                    for b in blocks_list:
                        if b.get("type") == "image" and b.get("local_image_path"):
                            count += 1
                        if b.get("children"):
                            count += count_images(b["children"])
                    return count

                page_images = count_images(blocks)
                if page_images > 0:
                    images_downloaded += page_images

            except Exception as e:
                print(f"  Warning: Could not get blocks for page {page_id}: {e}")
                page_data["blocks"] = []

            export_data["pages"].append(page_data)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\nExport complete!")
        print(f"  File: {output_file}")
        print(f"  Pages: {len(pages)}")
        print(f"  Images downloaded: {images_downloaded}")
        return export_data


def main():
    """Main function to run exports"""
    import sys

    # Get API token from environment variable
    api_token = os.getenv("NOTION_API_TOKEN")

    if not api_token:
        print("ERROR: NOTION_API_TOKEN environment variable not set")
        return

    # Get database ID from command line or prompt
    if len(sys.argv) > 1:
        database_id = sys.argv[1].strip()
    else:
        database_id = input("Enter Notion Database ID: ").strip()

    output_file = f"notion_export_with_images_{database_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    exporter = NotionExporterWithImages(api_token, image_dir="notion_images")

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
