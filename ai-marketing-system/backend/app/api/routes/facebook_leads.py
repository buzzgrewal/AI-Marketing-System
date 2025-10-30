"""
Facebook Lead Ads API Routes

Endpoints for managing Facebook Lead Ads integration and syncing leads.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_active_user
from app.services.facebook_lead_ads import facebook_lead_ads_service
from app.schemas.facebook_leads import (
    FacebookVerifyResponse,
    FacebookPageResponse,
    FacebookLeadFormResponse,
    FacebookFormDetailsResponse,
    FacebookSyncRequest,
    FacebookSyncResponse
)

router = APIRouter()


@router.get("/verify", response_model=FacebookVerifyResponse)
async def verify_facebook_credentials():
    """Verify Facebook access token and permissions"""
    try:
        result = await facebook_lead_ads_service.verify_credentials()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify Facebook credentials: {str(e)}"
        )


@router.get("/pages", response_model=List[FacebookPageResponse])
async def get_facebook_pages():
    """Get all Facebook Pages the user manages"""
    try:
        pages = await facebook_lead_ads_service.get_pages()
        return pages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Facebook Pages: {str(e)}"
        )


@router.get("/pages/{page_id}/forms", response_model=List[FacebookLeadFormResponse])
async def get_page_lead_forms(page_id: str):
    """Get all Lead Ad forms for a specific Facebook Page"""
    try:
        forms = await facebook_lead_ads_service.get_lead_forms(page_id)
        return forms
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch lead forms: {str(e)}"
        )


@router.get("/forms/{form_id}", response_model=FacebookFormDetailsResponse)
async def get_form_details(form_id: str):
    """Get detailed information about a specific Lead Ad form"""
    try:
        form_details = await facebook_lead_ads_service.get_form_details(form_id)
        return form_details
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Form not found: {str(e)}"
        )


@router.post("/forms/{form_id}/sync", response_model=FacebookSyncResponse)
async def sync_form_leads(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Sync leads from a Facebook Lead Ad form to the database"""
    try:
        result = await facebook_lead_ads_service.sync_leads_to_database(
            form_id=form_id,
            db=db,
            user_id=current_user.id if current_user else None
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync leads: {str(e)}"
        )


@router.get("/forms/{form_id}/preview")
async def preview_form_leads(form_id: str):
    """Preview leads from a form without saving to database"""
    try:
        leads = await facebook_lead_ads_service.get_leads_from_form(form_id, limit=10)
        return {
            "form_id": form_id,
            "preview_count": len(leads),
            "leads": leads
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview leads: {str(e)}"
        )
