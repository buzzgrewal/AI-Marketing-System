from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ShopifyStoreInfo(BaseModel):
    """Basic store information"""
    id: int
    name: str
    store_url: str
    configured: bool
    shop_name: Optional[str] = None
    email: Optional[str] = None
    domain: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    plan_name: Optional[str] = None
    created_at: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ShopifyStoreListItem(BaseModel):
    """Store list item"""
    id: int
    name: str
    store_url: str
    configured: bool


class ShopifyMetrics(BaseModel):
    """Store metrics"""
    total_customers: int
    total_orders: int
    total_products: int


class ShopifyShopInfo(BaseModel):
    """Detailed shop information"""
    name: Optional[str] = None
    email: Optional[str] = None
    domain: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    plan_name: Optional[str] = None
    country: Optional[str] = None


class ShopifyAuditResponse(BaseModel):
    """Comprehensive store audit response"""
    store_id: int
    store_name: str
    configured: bool
    audit_timestamp: Optional[str] = None
    shop_info: Optional[ShopifyShopInfo] = None
    metrics: Optional[ShopifyMetrics] = None
    status: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class ShopifyCustomer(BaseModel):
    """Shopify customer data"""
    id: int
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    accepts_marketing: bool = False
    orders_count: int = 0
    total_spent: Optional[str] = None
    created_at: Optional[str] = None


class ShopifySyncRequest(BaseModel):
    """Request to sync customers to leads"""
    store_id: int


class ShopifySyncResponse(BaseModel):
    """Response from customer sync operation"""
    success: bool
    synced: int
    skipped: int
    errors: int
    total_processed: Optional[int] = 0
    error: Optional[str] = None
