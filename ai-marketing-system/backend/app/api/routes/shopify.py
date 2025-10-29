from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.shopify_service import shopify_service
from app.schemas.shopify import (
    ShopifyStoreListItem,
    ShopifyStoreInfo,
    ShopifyAuditResponse,
    ShopifySyncRequest,
    ShopifySyncResponse
)

router = APIRouter()


@router.get("/stores", response_model=List[ShopifyStoreListItem])
async def get_stores():
    """Get list of all configured Shopify stores"""
    stores = shopify_service.get_all_stores()
    return stores


@router.get("/stores/{store_id}", response_model=ShopifyStoreInfo)
async def get_store_info(
    store_id: int
):
    """Get detailed information about a specific store"""
    try:
        store_info = await shopify_service.get_store_info(store_id)
        return store_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores/{store_id}/audit", response_model=ShopifyAuditResponse)
async def audit_store(
    store_id: int
):
    """Perform comprehensive audit of a Shopify store

    Returns:
    - Store information
    - Customer count
    - Order count
    - Product count
    - Store health status
    """
    try:
        audit_result = await shopify_service.audit_store(store_id)
        return audit_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stores/{store_id}/sync-customers", response_model=ShopifySyncResponse)
async def sync_customers_to_leads(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Sync Shopify customers to marketing leads database

    This will:
    1. Fetch customers from Shopify store
    2. Import them as leads in the marketing system
    3. Set email consent based on accepts_marketing flag
    4. Skip duplicate emails

    Returns sync statistics (synced, skipped, errors)

    Note: Using default user_id=1 for testing. In production, re-enable authentication.
    """
    try:
        # Use default user_id=1 for testing (remove auth requirement temporarily)
        result = await shopify_service.sync_customers_to_leads(
            store_id=store_id,
            user_id=1,  # Default user ID for testing
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores/{store_id}/customers")
async def get_customers(
    store_id: int,
    limit: int = 50
):
    """Get customers from Shopify store (raw data)"""
    try:
        customers = await shopify_service.get_customers(store_id, limit=limit)
        return {"customers": customers, "count": len(customers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores/{store_id}/orders")
async def get_orders(
    store_id: int,
    limit: int = 50,
    status: str = "any"
):
    """Get orders from Shopify store"""
    try:
        orders = await shopify_service.get_orders(store_id, limit=limit, status=status)
        return {"orders": orders, "count": len(orders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stores/{store_id}/products")
async def get_products(
    store_id: int,
    limit: int = 50
):
    """Get products from Shopify store"""
    try:
        products = await shopify_service.get_products(store_id, limit=limit)
        return {"products": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
