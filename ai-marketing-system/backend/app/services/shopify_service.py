import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.core.config import settings


class ShopifyService:
    """Service for interacting with Shopify Admin API"""

    def __init__(self):
        self.stores = [
            {
                "id": 1,
                "name": "Premier Bike",
                "store_url": settings.SHOPIFY_STORE_URL_1,
                "api_key": settings.SHOPIFY_API_KEY_1,
                "access_token": settings.SHOPIFY_ACCESS_TOKEN_1,
            },
            {
                "id": 2,
                "name": "Position One Sports",
                "store_url": settings.SHOPIFY_STORE_URL_2,
                "api_key": settings.SHOPIFY_API_KEY_2,
                "access_token": settings.SHOPIFY_ACCESS_TOKEN_2,
            }
        ]

    def _get_store_config(self, store_id: int) -> Optional[Dict[str, Any]]:
        """Get store configuration by ID"""
        for store in self.stores:
            if store["id"] == store_id:
                return store
        return None

    def _is_store_configured(self, store: Dict[str, Any]) -> bool:
        """Check if store has valid configuration"""
        return (
            store["store_url"]
            and store["access_token"]
            and store["store_url"] != ""
            and store["access_token"] != ""
            and not store["access_token"].startswith("your-")
        )

    async def _make_shopify_request(
        self,
        store_id: int,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to Shopify Admin API"""
        store = self._get_store_config(store_id)

        if not store:
            raise Exception(f"Store with ID {store_id} not found")

        if not self._is_store_configured(store):
            raise Exception(f"Store {store['name']} is not properly configured. Please set SHOPIFY credentials in .env")

        # Shopify Admin API base URL
        base_url = f"https://{store['store_url']}/admin/api/2024-01"
        url = f"{base_url}/{endpoint}"

        headers = {
            "X-Shopify-Access-Token": store["access_token"],
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                else:
                    response = await client.request(method, url, headers=headers, json=params)

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                print(f"Shopify API error: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Shopify API error: {e.response.status_code}")
            except Exception as e:
                print(f"Error making Shopify request: {str(e)}")
                raise Exception(f"Failed to connect to Shopify: {str(e)}")

    async def get_store_info(self, store_id: int) -> Dict[str, Any]:
        """Get basic store information"""
        store = self._get_store_config(store_id)

        if not store:
            raise Exception(f"Store with ID {store_id} not found")

        if not self._is_store_configured(store):
            return {
                "id": store_id,
                "name": store["name"],
                "store_url": store["store_url"],
                "configured": False,
                "message": "Store credentials not configured"
            }

        try:
            # Get shop info
            shop_data = await self._make_shopify_request(store_id, "shop.json")
            shop = shop_data.get("shop", {})

            return {
                "id": store_id,
                "name": store["name"],
                "store_url": store["store_url"],
                "configured": True,
                "shop_name": shop.get("name"),
                "email": shop.get("email"),
                "domain": shop.get("domain"),
                "currency": shop.get("currency"),
                "timezone": shop.get("iana_timezone"),
                "plan_name": shop.get("plan_name"),
                "created_at": shop.get("created_at"),
            }
        except Exception as e:
            return {
                "id": store_id,
                "name": store["name"],
                "store_url": store["store_url"],
                "configured": False,
                "error": str(e)
            }

    async def audit_store(self, store_id: int) -> Dict[str, Any]:
        """Perform comprehensive audit of a Shopify store"""
        store = self._get_store_config(store_id)

        if not store:
            raise Exception(f"Store with ID {store_id} not found")

        if not self._is_store_configured(store):
            return {
                "store_id": store_id,
                "store_name": store["name"],
                "configured": False,
                "message": "Store credentials not configured. Please add API credentials to .env file."
            }

        try:
            # Fetch multiple endpoints in parallel for audit
            shop_data = await self._make_shopify_request(store_id, "shop.json")
            customers_data = await self._make_shopify_request(
                store_id,
                "customers/count.json"
            )
            orders_data = await self._make_shopify_request(
                store_id,
                "orders/count.json",
                params={"status": "any"}
            )
            products_data = await self._make_shopify_request(
                store_id,
                "products/count.json"
            )

            shop = shop_data.get("shop", {})

            return {
                "store_id": store_id,
                "store_name": store["name"],
                "configured": True,
                "audit_timestamp": datetime.now().isoformat(),
                "shop_info": {
                    "name": shop.get("name"),
                    "email": shop.get("email"),
                    "domain": shop.get("domain"),
                    "currency": shop.get("currency"),
                    "timezone": shop.get("iana_timezone"),
                    "plan_name": shop.get("plan_name"),
                    "country": shop.get("country_name"),
                },
                "metrics": {
                    "total_customers": customers_data.get("count", 0),
                    "total_orders": orders_data.get("count", 0),
                    "total_products": products_data.get("count", 0),
                },
                "status": "healthy"
            }
        except Exception as e:
            print(f"Error auditing store: {str(e)}")
            return {
                "store_id": store_id,
                "store_name": store["name"],
                "configured": True,
                "error": str(e),
                "status": "error"
            }

    async def get_customers(
        self,
        store_id: int,
        limit: int = 50,
        since_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get customers from Shopify store"""
        params = {"limit": min(limit, 250)}
        if since_id:
            params["since_id"] = since_id

        try:
            result = await self._make_shopify_request(
                store_id,
                "customers.json",
                params=params
            )
            return result.get("customers", [])
        except Exception as e:
            print(f"Error fetching customers: {str(e)}")
            return []

    async def get_orders(
        self,
        store_id: int,
        limit: int = 50,
        status: str = "any"
    ) -> List[Dict[str, Any]]:
        """Get orders from Shopify store"""
        params = {
            "limit": min(limit, 250),
            "status": status
        }

        try:
            result = await self._make_shopify_request(
                store_id,
                "orders.json",
                params=params
            )
            return result.get("orders", [])
        except Exception as e:
            print(f"Error fetching orders: {str(e)}")
            return []

    async def get_products(
        self,
        store_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get products from Shopify store"""
        params = {"limit": min(limit, 250)}

        try:
            result = await self._make_shopify_request(
                store_id,
                "products.json",
                params=params
            )
            return result.get("products", [])
        except Exception as e:
            print(f"Error fetching products: {str(e)}")
            return []

    async def sync_customers_to_leads(
        self,
        store_id: int,
        user_id: int,
        db
    ) -> Dict[str, Any]:
        """Sync Shopify customers to marketing leads database"""
        from app.models.lead import Lead, LeadSource

        try:
            customers = await self.get_customers(store_id, limit=250)

            synced = 0
            skipped = 0
            errors = 0

            for customer in customers:
                try:
                    # Check if customer already exists
                    email = customer.get("email")
                    if not email:
                        skipped += 1
                        continue

                    existing_lead = db.query(Lead).filter(
                        Lead.email == email,
                        Lead.user_id == user_id
                    ).first()

                    if existing_lead:
                        skipped += 1
                        continue

                    # Create new lead from Shopify customer
                    lead = Lead(
                        user_id=user_id,
                        name=f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or "Unknown",
                        email=email,
                        phone=customer.get("phone"),
                        source=LeadSource.SHOPIFY,
                        email_consent=customer.get("accepts_marketing", False),
                        sms_consent=customer.get("accepts_marketing_updated_at") is not None,
                        consent_date=datetime.now() if customer.get("accepts_marketing") else None,
                        consent_source="shopify_import",
                        notes=f"Imported from Shopify. Total orders: {customer.get('orders_count', 0)}"
                    )

                    db.add(lead)
                    synced += 1

                except Exception as e:
                    print(f"Error syncing customer {customer.get('id')}: {str(e)}")
                    errors += 1
                    continue

            db.commit()

            return {
                "success": True,
                "synced": synced,
                "skipped": skipped,
                "errors": errors,
                "total_processed": len(customers)
            }

        except Exception as e:
            print(f"Error syncing customers: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "synced": 0,
                "skipped": 0,
                "errors": 0
            }

    def get_all_stores(self) -> List[Dict[str, Any]]:
        """Get list of all configured stores"""
        return [
            {
                "id": store["id"],
                "name": store["name"],
                "store_url": store["store_url"],
                "configured": self._is_store_configured(store)
            }
            for store in self.stores
        ]


# Singleton instance
shopify_service = ShopifyService()
