#!/usr/bin/env python3
"""
List all Notion databases accessible to your integration.
"""

import requests
import sys

def list_databases(api_token: str):
    """List all databases the integration has access to"""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    url = "https://api.notion.com/v1/search"
    payload = {
        "filter": {
            "value": "database",
            "property": "object"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        databases = data.get("results", [])

        if not databases:
            print("\nNo databases found.")
            print("\nMake sure you've shared your databases with the integration:")
            print("1. Open the database in Notion")
            print("2. Click '...' menu → 'Add connections'")
            print("3. Select your integration")
            return

        print(f"\nFound {len(databases)} database(s):\n")

        for i, db in enumerate(databases, 1):
            title = ""
            if "title" in db and len(db["title"]) > 0:
                title = db["title"][0].get("plain_text", "Untitled")

            print(f"{i}. {title}")
            print(f"   ID: {db['id']}")
            print(f"   URL: {db.get('url', 'N/A')}")
            print()

    except requests.exceptions.HTTPError as e:
        print(f"\nERROR: {e}")
        print(f"Response: {e.response.text}")
        print("\nMake sure your API token is valid and databases are shared with the integration.")
    except Exception as e:
        print(f"\nERROR: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = input("Enter your Notion API token: ").strip()

    list_databases(token)
