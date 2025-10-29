#!/usr/bin/env python3
"""
Test script for Shopify integration

This script verifies that your Shopify credentials are correctly configured
and tests the connection to your Shopify stores.

Usage:
    python test_shopify_integration.py
"""

import asyncio
import sys
from app.core.config import settings
from app.services.shopify_service import shopify_service


async def test_store(store_id: int, store_name: str):
    """Test a specific Shopify store"""
    print(f"\n{'='*60}")
    print(f"Testing {store_name} (Store {store_id})")
    print(f"{'='*60}\n")

    # Get store configuration
    store_config = shopify_service._get_store_config(store_id)

    if not store_config:
        print(f"❌ Store {store_id} configuration not found")
        return False

    print(f"Store URL: {store_config['store_url']}")
    print(f"API Key: {store_config['api_key'][:10]}..." if len(store_config['api_key']) > 10 else f"API Key: {store_config['api_key']}")
    print(f"Access Token: {store_config['access_token'][:20]}..." if len(store_config['access_token']) > 20 else f"Access Token: {store_config['access_token']}")
    print()

    # Check if configured
    if not shopify_service._is_store_configured(store_config):
        print("❌ Store is not properly configured")
        print("   Please update the following in your .env file:")
        print(f"   - SHOPIFY_STORE_URL_{store_id}")
        print(f"   - SHOPIFY_API_KEY_{store_id}")
        print(f"   - SHOPIFY_ACCESS_TOKEN_{store_id}")
        return False

    print("✓ Store credentials are configured\n")

    # Test connection by fetching store info
    print("1. Testing connection...")
    try:
        store_info = await shopify_service.get_store_info(store_id)

        if not store_info.get('configured'):
            print(f"❌ Failed to connect: {store_info.get('error', store_info.get('message', 'Unknown error'))}")
            print("\nTroubleshooting:")
            print("- Verify your access token is valid")
            print("- Ensure the store URL is correct (format: yourstore.myshopify.com)")
            print("- Check that the access token has admin API access")
            return False

        print("✓ Successfully connected to Shopify!")
        print(f"\nStore Details:")
        print(f"  Name: {store_info.get('shop_name')}")
        print(f"  Email: {store_info.get('email')}")
        print(f"  Domain: {store_info.get('domain')}")
        print(f"  Currency: {store_info.get('currency')}")
        print(f"  Timezone: {store_info.get('timezone')}")
        print(f"  Plan: {store_info.get('plan_name')}")
        print(f"  Created: {store_info.get('created_at')}")

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

    # Perform audit
    print("\n2. Performing store audit...")
    try:
        audit = await shopify_service.audit_store(store_id)

        if audit.get('status') == 'error':
            print(f"❌ Audit failed: {audit.get('error')}")
            return False

        metrics = audit.get('metrics', {})
        print("✓ Audit completed successfully!")
        print(f"\nStore Metrics:")
        print(f"  Total Customers: {metrics.get('total_customers', 0)}")
        print(f"  Total Orders: {metrics.get('total_orders', 0)}")
        print(f"  Total Products: {metrics.get('total_products', 0)}")

    except Exception as e:
        print(f"❌ Audit failed: {str(e)}")
        return False

    # Test fetching customers
    print("\n3. Testing customer data retrieval...")
    try:
        customers = await shopify_service.get_customers(store_id, limit=5)
        print(f"✓ Successfully retrieved {len(customers)} customers (sample)")

        if customers:
            print("\nSample Customer:")
            customer = customers[0]
            print(f"  ID: {customer.get('id')}")
            print(f"  Name: {customer.get('first_name')} {customer.get('last_name')}")
            print(f"  Email: {customer.get('email')}")
            print(f"  Phone: {customer.get('phone', 'N/A')}")
            print(f"  Orders: {customer.get('orders_count', 0)}")
            print(f"  Accepts Marketing: {customer.get('accepts_marketing', False)}")
        else:
            print("  (No customers found in store)")

    except Exception as e:
        print(f"❌ Failed to retrieve customers: {str(e)}")
        return False

    # Test fetching orders
    print("\n4. Testing order data retrieval...")
    try:
        orders = await shopify_service.get_orders(store_id, limit=5)
        print(f"✓ Successfully retrieved {len(orders)} orders (sample)")

        if orders:
            print("\nSample Order:")
            order = orders[0]
            print(f"  Order #: {order.get('order_number')}")
            print(f"  Name: {order.get('name')}")
            print(f"  Total: {order.get('currency')} {order.get('total_price')}")
            print(f"  Status: {order.get('financial_status')}")
            print(f"  Date: {order.get('created_at')}")
        else:
            print("  (No orders found in store)")

    except Exception as e:
        print(f"❌ Failed to retrieve orders: {str(e)}")
        return False

    # Test fetching products
    print("\n5. Testing product data retrieval...")
    try:
        products = await shopify_service.get_products(store_id, limit=5)
        print(f"✓ Successfully retrieved {len(products)} products (sample)")

        if products:
            print("\nSample Product:")
            product = products[0]
            print(f"  ID: {product.get('id')}")
            print(f"  Title: {product.get('title')}")
            print(f"  Vendor: {product.get('vendor')}")
            print(f"  Product Type: {product.get('product_type')}")
            print(f"  Status: {product.get('status')}")
        else:
            print("  (No products found in store)")

    except Exception as e:
        print(f"❌ Failed to retrieve products: {str(e)}")
        return False

    print(f"\n{'='*60}")
    print(f"✓ All tests passed for {store_name}!")
    print(f"{'='*60}")

    return True


async def main():
    print("="*60)
    print("Shopify Integration Test")
    print("="*60)
    print()

    # Get all stores
    stores = shopify_service.get_all_stores()

    print("Configured Stores:")
    for store in stores:
        status = "✓ Configured" if store['configured'] else "❌ Not Configured"
        print(f"  {store['id']}. {store['name']} ({store['store_url']}) - {status}")
    print()

    # Test each configured store
    results = {}
    for store in stores:
        if store['configured']:
            result = await test_store(store['id'], store['name'])
            results[store['id']] = result
        else:
            print(f"\nSkipping {store['name']} (not configured)")
            results[store['id']] = None

    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    configured_count = sum(1 for r in results.values() if r is not None)
    passed_count = sum(1 for r in results.values() if r is True)

    print(f"\nConfigured Stores: {configured_count}/{len(stores)}")
    print(f"Tests Passed: {passed_count}/{configured_count if configured_count > 0 else 0}")

    if passed_count == configured_count and configured_count > 0:
        print("\n🎉 All configured stores are working correctly!")
        print("\nYou can now:")
        print("  - Sync customers to your leads database")
        print("  - View store analytics and metrics")
        print("  - Access order and product data")
        print("\nNext steps:")
        print("1. Start the backend: cd backend && python main.py")
        print("2. Use the API endpoints:")
        print("   - GET /api/shopify/stores - List stores")
        print("   - GET /api/shopify/stores/{id}/audit - Audit store")
        print("   - POST /api/shopify/stores/{id}/sync-customers - Sync customers")
    elif configured_count == 0:
        print("\n⚠ No stores are configured yet")
        print("\nTo configure a store:")
        print("1. Get your Shopify Admin API access token")
        print("2. Add credentials to backend/.env:")
        print("   SHOPIFY_STORE_URL_1=yourstore.myshopify.com")
        print("   SHOPIFY_API_KEY_1=your-api-key")
        print("   SHOPIFY_ACCESS_TOKEN_1=your-access-token")
    else:
        print("\n⚠ Some tests failed")
        print("Please check the error messages above and verify your credentials")

    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
