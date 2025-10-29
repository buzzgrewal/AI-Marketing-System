# Shopify Integration Guide

This guide explains how to integrate your Shopify store(s) with the AI Marketing Automation System to sync customers, access order data, and use store information for marketing campaigns.

## Overview

The Shopify integration enables:
- ✅ **Customer Sync** - Automatically import Shopify customers as marketing leads
- ✅ **Order Data Access** - View and analyze order history
- ✅ **Product Catalog** - Access product information for marketing content
- ✅ **Store Metrics** - Monitor customer count, order count, and product count
- ✅ **Consent Tracking** - Respect customer marketing preferences from Shopify
- ✅ **Multi-Store Support** - Connect up to 2 Shopify stores

## Prerequisites

1. **Shopify Store** - You need a Shopify store with Admin access
2. **Custom App** - Create a custom app in your Shopify admin
3. **Admin API Access Token** - Generate an access token with proper permissions

## Setup Instructions

### Step 1: Create a Custom App in Shopify

1. Log in to your Shopify admin panel
2. Go to **Settings** → **Apps and sales channels**
3. Click **Develop apps** (or **Develop apps for your store**)
4. If this is your first custom app, click **Allow custom app development**
5. Click **Create an app**
6. Enter app details:
   - **App name**: AI Marketing Automation (or any name you prefer)
   - **App developer**: Your name or company
7. Click **Create app**

### Step 2: Configure Admin API Scopes

After creating the app, you need to configure permissions:

1. Click on **Configuration** tab
2. Under **Admin API integration**, click **Configure**
3. Select the following scopes (permissions):

   **Required Permissions:**
   - `read_customers` - Read customer data
   - `read_orders` - Read order data
   - `read_products` - Read product catalog
   - `read_inventory` - Read inventory levels

   **Optional (Recommended):**
   - `read_analytics` - Access store analytics
   - `read_reports` - Access store reports

4. Click **Save**

### Step 3: Install the App and Get Access Token

1. Click on the **API credentials** tab
2. Under **Access tokens**, click **Install app**
3. Click **Install** to confirm
4. Your **Admin API access token** will be revealed
5. **IMPORTANT**: Copy this token immediately - you won't be able to see it again!
6. Also note your **API key** (shown at the top)

Your credentials should look like this:
- **API Key**: `a3b405100e4c8666e3e0bfe9a5e83931` (hexadecimal string)
- **Access Token**: `shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (starts with `shpat_`)

### Step 4: Find Your Store URL

Your store URL is your Shopify domain in the format:
```
yourstore.myshopify.com
```

For example:
- `position-one.myshopify.com`
- `premierbike.myshopify.com`

You can find this in your Shopify admin URL or in Settings → Domains.

### Step 5: Configure Backend (.env)

Add your credentials to `backend/.env`:

**For Store 1:**
```bash
SHOPIFY_STORE_URL_1=premierbike.myshopify.com
SHOPIFY_API_KEY_1=a3b405100e4c8666e3e0bfe9a5e83931
SHOPIFY_ACCESS_TOKEN_1=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**For Store 2:**
```bash
SHOPIFY_STORE_URL_2=position-one.myshopify.com
SHOPIFY_API_KEY_2=a3b405100e4c8666e3e0bfe9a5e83931
SHOPIFY_ACCESS_TOKEN_2=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Important Notes:**
- Replace `yourstore.myshopify.com` with your actual Shopify domain
- Replace the API key and access token with your actual credentials
- Access tokens starting with `shpss_` are **storefront tokens** - you need `shpat_` (Admin API tokens)
- If you only have one store, you can leave Store 1 credentials as placeholders

### Step 6: Verify Your Setup

Run the test script to verify everything is configured correctly:

```bash
cd backend
python test_shopify_integration.py
```

You should see output like:
```
✓ Store credentials are configured
✓ Successfully connected to Shopify!

Store Details:
  Name: Position One Sports
  Email: support@positiononesports.com
  Domain: position-one.myshopify.com
  Currency: USD
  ...

Store Metrics:
  Total Customers: 156
  Total Orders: 342
  Total Products: 89
```

## Common Issues and Troubleshooting

### Error: "Invalid API key or access token"

**Cause**: The access token is invalid, expired, or is a storefront token instead of an admin token.

**Solution:**
1. Verify you're using an **Admin API access token** (starts with `shpat_`)
2. **Storefront tokens** (start with `shpss_`) will NOT work - you need an admin token
3. Re-generate the access token:
   - Go to Shopify Admin → Settings → Apps and sales channels
   - Click on your custom app
   - Go to API credentials tab
   - Under "Admin API access token", you may need to uninstall and reinstall the app to get a new token

### Error: "Store credentials not configured"

**Cause**: Missing or placeholder credentials in `.env` file.

**Solution:**
- Check that `SHOPIFY_STORE_URL_2`, `SHOPIFY_API_KEY_2`, and `SHOPIFY_ACCESS_TOKEN_2` are set
- Ensure values don't start with "your-" (which indicates placeholders)
- Remove any quotes around the values

### Error: "Store with ID X not found"

**Cause**: Invalid store ID in API request.

**Solution:**
- Use store ID `1` for the first store or `2` for the second store
- Check which stores are configured: `GET /api/shopify/stores`

### Store URL Format

**Correct format:**
```
position-one.myshopify.com
```

**Incorrect formats:**
```
https://position-one.myshopify.com  ❌ (don't include protocol)
position-one.com                     ❌ (use .myshopify.com domain)
www.position-one.myshopify.com      ❌ (no www)
```

## Using the Integration

### Via API Endpoints

Once configured, you can use these endpoints:

#### 1. List Configured Stores
```bash
GET /api/shopify/stores
```

Response:
```json
{
  "stores": [
    {
      "id": 1,
      "name": "Premier Bike",
      "store_url": "premierbike.myshopify.com",
      "configured": false
    },
    {
      "id": 2,
      "name": "Position One Sports",
      "store_url": "position-one.myshopify.com",
      "configured": true
    }
  ]
}
```

#### 2. Get Store Details
```bash
GET /api/shopify/stores/2
```

Response:
```json
{
  "id": 2,
  "name": "Position One Sports",
  "store_url": "position-one.myshopify.com",
  "configured": true,
  "shop_name": "Position One Sports",
  "email": "support@positiononesports.com",
  "domain": "position-one.myshopify.com",
  "currency": "USD",
  "timezone": "America/New_York",
  "plan_name": "Basic",
  "created_at": "2020-01-15T10:30:00-05:00"
}
```

#### 3. Audit Store (Get Metrics)
```bash
GET /api/shopify/stores/2/audit
```

Response:
```json
{
  "store_id": 2,
  "store_name": "Position One Sports",
  "configured": true,
  "audit_timestamp": "2025-10-29T15:30:00",
  "shop_info": {
    "name": "Position One Sports",
    "email": "support@positiononesports.com",
    "domain": "position-one.myshopify.com",
    "currency": "USD",
    "timezone": "America/New_York",
    "plan_name": "Basic",
    "country": "United States"
  },
  "metrics": {
    "total_customers": 156,
    "total_orders": 342,
    "total_products": 89
  },
  "status": "healthy"
}
```

#### 4. Sync Customers to Leads Database
```bash
POST /api/shopify/stores/2/sync-customers
```

This is the **main feature** - it imports your Shopify customers as marketing leads.

Response:
```json
{
  "success": true,
  "synced": 45,
  "skipped": 111,
  "errors": 0,
  "total_processed": 156
}
```

**How it works:**
- Fetches up to 250 customers from Shopify
- Creates a new Lead record for each customer
- Skips customers that already exist in your database (based on email)
- Respects customer's marketing consent (`accepts_marketing` flag)
- Sets lead source as "Shopify"
- Adds order count to notes field

**Consent Handling:**
- If customer has `accepts_marketing: true` in Shopify → Lead gets `email_consent: true`
- If customer has `accepts_marketing: false` → Lead gets `email_consent: false`
- This ensures **CAN-SPAM compliance** - you won't email customers who opted out

#### 5. Get Customers (Raw Data)
```bash
GET /api/shopify/stores/2/customers?limit=50
```

Fetches raw customer data from Shopify without syncing to database.

Response:
```json
{
  "customers": [
    {
      "id": 1234567890,
      "email": "customer@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone": "+1234567890",
      "accepts_marketing": true,
      "orders_count": 5,
      "total_spent": "542.50",
      "created_at": "2023-06-15T10:30:00-05:00"
    }
  ]
}
```

#### 6. Get Orders
```bash
GET /api/shopify/stores/2/orders?limit=50&status=any
```

Status options: `open`, `closed`, `cancelled`, `any`

Response:
```json
{
  "orders": [
    {
      "id": 9876543210,
      "order_number": 1001,
      "name": "#1001",
      "total_price": "125.00",
      "currency": "USD",
      "financial_status": "paid",
      "fulfillment_status": "fulfilled",
      "created_at": "2025-10-25T14:22:00-05:00",
      "customer": {
        "email": "customer@example.com"
      }
    }
  ]
}
```

#### 7. Get Products
```bash
GET /api/shopify/stores/2/products?limit=50
```

Response:
```json
{
  "products": [
    {
      "id": 1122334455,
      "title": "Road Bike - Carbon Frame",
      "vendor": "Trek",
      "product_type": "Bicycles",
      "status": "active",
      "variants": [
        {
          "id": 5566778899,
          "title": "Medium",
          "price": "2499.00",
          "sku": "BIKE-001-M",
          "inventory_quantity": 5
        }
      ]
    }
  ]
}
```

### Via Web Interface

1. Start the backend and frontend:
   ```bash
   # Terminal 1 - Backend
   cd backend
   python main.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. Log in to the web app
3. Navigate to **Integrations** → **Shopify**
4. You'll see your configured stores
5. Click **Sync Customers** to import customers as leads
6. View the imported leads in the **Leads** page

## Data Sync Details

### What Gets Synced

When you sync customers from Shopify, the following data is imported:

| Shopify Field | Marketing Lead Field | Notes |
|---------------|---------------------|-------|
| `email` | `email` | Primary identifier |
| `first_name` + `last_name` | `name` | Combined into full name |
| `phone` | `phone` | Direct copy |
| `accepts_marketing` | `email_consent` | Respects customer preference |
| `accepts_marketing` | `sms_consent` | If marketing updated |
| `orders_count` | `notes` | "Total orders: X" |
| - | `source` | Set to "shopify" |
| - | `consent_source` | Set to "shopify_import" |
| - | `consent_date` | Set to now (if accepts marketing) |

### Deduplication

The system prevents duplicate leads:
- Checks if email already exists in your database
- If email exists → skips customer (shows in "skipped" count)
- If email is new → creates new lead (shows in "synced" count)

### Customer Privacy & Consent

The integration is **fully compliant** with privacy laws:

1. **CAN-SPAM Act**: Only customers with `accepts_marketing: true` get `email_consent: true`
2. **GDPR**: Respects customer's marketing preferences from Shopify
3. **Consent Tracking**: Records consent date and source for audit trail
4. **Opt-Out Support**: Customers who unsubscribed in Shopify won't receive marketing emails

## Multi-Store Management

You can connect up to 2 Shopify stores:

**Use Cases:**
- Multiple brands under same business
- Different product categories (e.g., bikes and accessories)
- Regional stores (e.g., US store and EU store)

**How it works:**
- Each store has its own credentials in `.env`
- Stores are identified by ID (1 or 2)
- Customer syncs are per-store (sync Store 1, then sync Store 2)
- Leads are tagged with source "shopify" (not per-store)

**To add more stores:**
- Currently limited to 2 stores in configuration
- To support more stores, update `backend/app/core/config.py` and `backend/app/services/shopify_service.py`

## API Rate Limits

Shopify has API rate limits:

**Shopify Plus:**
- 4 requests per second
- Burst allowance: 80 requests

**Regular Shopify:**
- 2 requests per second
- Burst allowance: 40 requests

The integration respects these limits by:
- Fetching data in batches (max 250 items per request)
- Not implementing aggressive retry logic
- Recommending scheduled syncs (not real-time)

## Best Practices

### 1. Schedule Regular Syncs

Instead of syncing manually, set up a scheduled task:

```python
# Example: Sync customers nightly at 2 AM
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.shopify_service import shopify_service

scheduler = AsyncIOScheduler()

async def sync_all_stores():
    # Sync store 2 (Position One Sports)
    await shopify_service.sync_customers_to_leads(2, user_id=1, db=db)

scheduler.add_job(sync_all_stores, 'cron', hour=2)
scheduler.start()
```

### 2. Monitor Sync Results

After each sync, check the results:
- `synced`: New customers added
- `skipped`: Existing customers (duplicates)
- `errors`: Failed imports

Investigate errors if count is high.

### 3. Segment by Source

In your marketing campaigns, you can filter leads by source:
```python
shopify_leads = db.query(Lead).filter(Lead.source == LeadSource.SHOPIFY).all()
```

This lets you create Shopify-specific campaigns.

### 4. Respect Consent

Always filter by `email_consent` before sending emails:
```python
leads_to_email = db.query(Lead).filter(
    Lead.source == LeadSource.SHOPIFY,
    Lead.email_consent == True
).all()
```

Never email customers without consent.

### 5. Keep Credentials Secure

- Never commit `.env` files to version control
- Use environment variables in production
- Rotate access tokens if compromised
- Use separate apps for dev/staging/production

## Testing Your Integration

### Manual Test via API

Use curl or Postman to test endpoints:

```bash
# Get store info
curl -X GET "http://localhost:8000/api/shopify/stores/2" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Sync customers
curl -X POST "http://localhost:8000/api/shopify/stores/2/sync-customers" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Automated Test Script

Run the provided test script:

```bash
cd backend
python test_shopify_integration.py
```

This will:
1. Check store configuration
2. Test connection to Shopify
3. Fetch sample data (customers, orders, products)
4. Report any errors

## Advanced Usage

### Custom Sync Logic

If you need custom sync behavior, modify `shopify_service.py`:

```python
# Example: Only sync customers who made a purchase in last 90 days
async def sync_active_customers(self, store_id: int, user_id: int, db):
    from datetime import timedelta

    customers = await self.get_customers(store_id, limit=250)

    for customer in customers:
        # Check last order date
        if customer.get('orders_count', 0) > 0:
            # Custom logic here
            pass
```

### Webhook Integration (Future Enhancement)

For real-time sync, consider Shopify webhooks:
1. Create webhook in Shopify admin
2. Point to your API endpoint
3. Process customer updates in real-time

Example webhook topics:
- `customers/create` - New customer
- `customers/update` - Customer updated
- `orders/create` - New order

## Support & Resources

### Shopify API Documentation
- [Admin API Reference](https://shopify.dev/docs/api/admin-rest)
- [Authentication Guide](https://shopify.dev/docs/apps/auth)
- [API Rate Limits](https://shopify.dev/docs/api/usage/rate-limits)

### Getting Help

If you encounter issues:
1. Run `test_shopify_integration.py` to diagnose
2. Check Shopify API logs in your app dashboard
3. Verify API scopes include required permissions
4. Check backend logs for error details

### Security & Privacy

- Store access tokens in secure environment variables
- Never log or display full access tokens
- Regularly audit API access in Shopify admin
- Implement proper authentication for API endpoints
- Follow Shopify's API Terms of Service

## Appendix: API Permissions Reference

### Required Scopes

| Scope | Purpose | Used For |
|-------|---------|----------|
| `read_customers` | Read customer data | Customer sync, customer list |
| `read_orders` | Read order data | Order history, revenue tracking |
| `read_products` | Read products | Product catalog, marketing content |

### Optional Scopes

| Scope | Purpose | Use Case |
|-------|---------|----------|
| `read_inventory` | Read stock levels | Product availability |
| `read_analytics` | Access analytics | Advanced reporting |
| `write_customers` | Update customers | Two-way sync (future) |

## Changelog

- **v1.0.0** (2025-10-29): Initial Shopify integration
  - Multi-store support (2 stores)
  - Customer sync with consent tracking
  - Order and product data access
  - Store audit and metrics
