#!/usr/bin/env python3
"""Test Facebook Lead Ads API Access"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def test_facebook_token():
    """Test if the Facebook token has Lead Ads permissions"""

    token = os.getenv('META_ACCESS_TOKEN')

    if not token:
        print("❌ No META_ACCESS_TOKEN found in .env")
        return

    # Test token validity and permissions
    debug_url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"

    response = requests.get(debug_url)
    data = response.json()

    if 'error' in data:
        print(f"❌ Token Error: {data['error'].get('message', 'Unknown error')}")
        return

    if 'data' in data:
        token_data = data['data']

        # Check if token is valid
        is_valid = token_data.get('is_valid', False)
        print(f"✅ Token Valid: {is_valid}" if is_valid else "❌ Token Invalid")

        # Check permissions
        scopes = token_data.get('scopes', [])
        print(f"\n📋 Current Permissions: {', '.join(scopes)}")

        # Check for Lead Ads permission
        has_leads = 'leads_retrieval' in scopes
        print(f"\n{'✅' if has_leads else '❌'} Lead Ads Permission (leads_retrieval): {'Found' if has_leads else 'MISSING'}")

        # Check other important permissions
        important_perms = {
            'pages_manage_ads': 'Page Ads Management',
            'pages_read_engagement': 'Page Engagement Reading',
            'ads_management': 'Ads Management',
            'business_management': 'Business Management'
        }

        print("\n📊 Other Permissions Status:")
        for perm, name in important_perms.items():
            has_perm = perm in scopes
            print(f"  {'✅' if has_perm else '❌'} {name} ({perm}): {'Found' if has_perm else 'Missing'}")

        # Check token expiry
        expires_at = token_data.get('expires_at', 0)
        if expires_at > 0:
            from datetime import datetime
            expiry = datetime.fromtimestamp(expires_at)
            print(f"\n⏰ Token Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}")

        # Get associated pages
        if has_leads:
            print("\n📄 Fetching associated pages...")
            pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={token}"
            pages_response = requests.get(pages_url)
            pages_data = pages_response.json()

            if 'data' in pages_data:
                print(f"Found {len(pages_data['data'])} page(s):")
                for page in pages_data['data']:
                    print(f"  - {page.get('name')} (ID: {page.get('id')})")

if __name__ == "__main__":
    print("🔍 Testing Facebook Lead Ads API Access\n")
    print("=" * 50)
    test_facebook_token()