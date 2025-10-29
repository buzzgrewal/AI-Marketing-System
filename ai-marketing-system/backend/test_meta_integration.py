#!/usr/bin/env python3
"""
Test script for Meta/Facebook integration

This script verifies that your Meta credentials are correctly configured
and tests the Facebook/Instagram posting functionality.

Usage:
    python test_meta_integration.py
"""

import asyncio
import sys
from app.core.config import settings
from app.services.social_scheduler import social_scheduler


async def main():
    print("=" * 60)
    print("Meta/Facebook Integration Test")
    print("=" * 60)
    print()

    # Check if credentials are configured
    print("1. Checking configuration...")
    if not settings.META_APP_ID:
        print("❌ META_APP_ID is not set")
        sys.exit(1)
    else:
        print(f"✓ META_APP_ID: {settings.META_APP_ID}")

    if not settings.META_APP_SECRET:
        print("❌ META_APP_SECRET is not set")
        sys.exit(1)
    else:
        print(f"✓ META_APP_SECRET: {'*' * len(settings.META_APP_SECRET)}")

    if not settings.META_ACCESS_TOKEN:
        print("❌ META_ACCESS_TOKEN is not set")
        sys.exit(1)
    else:
        print(f"✓ META_ACCESS_TOKEN: {settings.META_ACCESS_TOKEN[:20]}...")

    print()

    # Verify token
    print("2. Verifying Meta access token...")
    result = await social_scheduler.verify_meta_token()

    if not result.get('valid'):
        print(f"❌ Token verification failed: {result.get('error')}")
        print()
        print("Troubleshooting:")
        print("- Ensure META_ACCESS_TOKEN is a Page Access Token (not User Token)")
        print("- Verify the token hasn't expired")
        print("- Check that required permissions are granted")
        sys.exit(1)

    print("✓ Token is valid!")
    print()

    # Display token details
    print("3. Token Details:")
    print(f"   App ID: {result.get('app_id')}")
    print(f"   Page ID: {result.get('page_id')}")
    print(f"   Page Name: {result.get('page_name')}")
    print(f"   Expires: {'Never' if result.get('expires_at') == 0 else result.get('expires_at')}")
    print()

    print("4. Permissions:")
    scopes = result.get('scopes', [])
    if scopes:
        for scope in scopes:
            print(f"   ✓ {scope}")
    else:
        print("   ⚠ No scopes found")
    print()

    # Check Instagram
    print("5. Instagram Integration:")
    if result.get('instagram_enabled'):
        print(f"   ✓ Instagram Business Account connected!")
        print(f"   Instagram Account ID: {result.get('instagram_account_id')}")
    else:
        print("   ⚠ No Instagram Business Account found")
        print("   To enable Instagram posting:")
        print("   1. Go to your Facebook Page settings")
        print("   2. Connect your Instagram Business Account")
        print("   3. Ensure it's a Business account (not Creator or Personal)")
    print()

    # Check required permissions
    print("6. Permission Check:")
    required_permissions = {
        'pages_manage_posts': 'Required for posting to Facebook',
        'pages_read_engagement': 'Required for reading metrics',
        'instagram_basic': 'Required for Instagram access',
        'instagram_content_publish': 'Required for Instagram posting'
    }

    missing_permissions = []
    for perm, description in required_permissions.items():
        if perm in scopes:
            print(f"   ✓ {perm}")
        else:
            print(f"   ❌ {perm} - {description}")
            missing_permissions.append(perm)

    print()

    if missing_permissions:
        print("⚠ Warning: Some permissions are missing")
        print("You may need to re-generate your access token with these permissions:")
        for perm in missing_permissions:
            print(f"  - {perm}")
        print()

    # Platform status
    print("7. Platform Status:")
    print(f"   Facebook: {'✓ Enabled' if social_scheduler.platforms_config['facebook']['enabled'] else '❌ Disabled'}")
    print(f"   Instagram: {'✓ Enabled' if social_scheduler.platforms_config['instagram']['enabled'] else '❌ Disabled'}")
    print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    all_good = True

    if not result.get('valid'):
        print("❌ Token is invalid")
        all_good = False
    else:
        print("✓ Meta integration is configured correctly")

    if result.get('instagram_enabled'):
        print("✓ Instagram posting is available")
    else:
        print("⚠ Instagram posting is not available (no Business account connected)")
        all_good = False

    if missing_permissions:
        print(f"⚠ Missing {len(missing_permissions)} required permission(s)")
        all_good = False

    print()

    if all_good and result.get('instagram_enabled'):
        print("🎉 All systems go! You can now:")
        print("   - Post to Facebook")
        print("   - Post to Instagram")
        print("   - Track engagement metrics")
    elif all_good:
        print("✓ Facebook posting is ready!")
        print("⚠ Connect Instagram Business Account to enable Instagram posting")
    else:
        print("⚠ Some issues need to be resolved")
        print("See the docs/META_INTEGRATION_GUIDE.md for detailed setup instructions")

    print()
    print("Next steps:")
    print("1. Start the backend: cd backend && python main.py")
    print("2. Test the API: http://localhost:8000/api/social-scheduling/meta/verify")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Create a test post from the Social Scheduling page")
    print()


if __name__ == "__main__":
    asyncio.run(main())
