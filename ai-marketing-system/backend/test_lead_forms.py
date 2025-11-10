#!/usr/bin/env python3
"""Test Facebook Lead Forms API directly"""

import asyncio
import httpx
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

async def test_lead_forms():
    """Test fetching lead forms for a specific page"""

    token = os.getenv('META_ACCESS_TOKEN')
    page_id = "858212064264610"  # The page ID from your error
    api_version = "v18.0"
    base_url = f"https://graph.facebook.com/{api_version}"

    if not token:
        print("❌ No META_ACCESS_TOKEN found in .env")
        return

    print(f"🔍 Testing Lead Forms API for Page ID: {page_id}\n")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Get all pages and their tokens
        print("\n1️⃣ Fetching pages with access tokens...")
        try:
            pages_response = await client.get(
                f"{base_url}/me/accounts",
                params={
                    "access_token": token,
                    "fields": "id,name,access_token,tasks"
                }
            )
            pages_response.raise_for_status()
            pages_data = pages_response.json()

            print(f"✅ Found {len(pages_data.get('data', []))} pages")

            # Find the specific page
            page_token = None
            page_name = None
            for page in pages_data.get("data", []):
                print(f"  - Page: {page.get('name')} (ID: {page.get('id')})")
                print(f"    Tasks: {page.get('tasks', [])}")
                if page.get("id") == page_id:
                    page_token = page.get("access_token")
                    page_name = page.get("name")
                    print(f"    ✅ THIS IS OUR TARGET PAGE")

            if not page_token:
                print(f"\n❌ Page {page_id} not found in your managed pages")
                print("Available page IDs:", [p.get('id') for p in pages_data.get('data', [])])
                return

            print(f"\n✅ Found page: {page_name}")
            print(f"✅ Page has access token: {'Yes' if page_token else 'No'}")

        except httpx.HTTPStatusError as e:
            print(f"❌ Failed to fetch pages: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            return
        except Exception as e:
            print(f"❌ Error fetching pages: {str(e)}")
            return

        # Step 2: Try to fetch lead forms with page token
        print(f"\n2️⃣ Fetching lead forms for page {page_id}...")
        try:
            forms_response = await client.get(
                f"{base_url}/{page_id}/leadgen_forms",
                params={
                    "access_token": page_token,  # Use page token
                    "fields": "id,name,status,leads_count,created_time"
                }
            )

            print(f"Response status: {forms_response.status_code}")

            if forms_response.status_code != 200:
                print(f"❌ Error response: {forms_response.text}")
            else:
                forms_data = forms_response.json()
                forms = forms_data.get("data", [])

                if forms:
                    print(f"✅ Found {len(forms)} lead forms:")
                    for form in forms:
                        print(f"\n  📋 Form: {form.get('name', 'Unnamed')}")
                        print(f"     ID: {form.get('id')}")
                        print(f"     Status: {form.get('status', 'Unknown')}")
                        print(f"     Leads Count: {form.get('leads_count', 0)}")
                        print(f"     Created: {form.get('created_time', 'Unknown')}")
                else:
                    print("⚠️ No lead forms found for this page")
                    print("\nPossible reasons:")
                    print("  1. The page has no lead forms created")
                    print("  2. Lead forms are not active")
                    print("  3. You need to create a lead form first")
                    print("\nTo create a lead form:")
                    print("  1. Go to Facebook Page > Publishing Tools > Forms Library")
                    print("  2. Or use Facebook Ads Manager to create a Lead Generation campaign")

        except httpx.HTTPStatusError as e:
            print(f"❌ Failed to fetch lead forms: {e.response.status_code}")
            error_data = e.response.json() if e.response.text else {}
            print(f"Error details: {json.dumps(error_data, indent=2)}")

            if "error" in error_data:
                error = error_data["error"]
                print(f"\nError Message: {error.get('message', 'Unknown')}")
                print(f"Error Type: {error.get('type', 'Unknown')}")
                print(f"Error Code: {error.get('code', 'Unknown')}")

                if error.get('code') == 100:
                    print("\n💡 This usually means:")
                    print("  - The page doesn't have Lead Ads enabled")
                    print("  - Or you need additional permissions")

        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_lead_forms())