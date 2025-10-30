"""
Facebook Lead Ads Schemas

Pydantic models for Facebook Lead Ads API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class FacebookVerifyResponse(BaseModel):
    """Response for Facebook credential verification"""
    verified: bool
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    has_leads_permission: Optional[bool] = None
    message: Optional[str] = None
    error: Optional[str] = None


class FacebookPageResponse(BaseModel):
    """Facebook Page information"""
    id: str
    name: str
    access_token: Optional[str] = None

    class Config:
        from_attributes = True


class FacebookLeadFormResponse(BaseModel):
    """Facebook Lead Ad form information"""
    id: str
    name: str
    status: Optional[str] = None
    leads_count: Optional[int] = 0
    created_time: Optional[str] = None

    class Config:
        from_attributes = True


class FacebookFormDetailsResponse(BaseModel):
    """Detailed Facebook Lead Ad form information"""
    id: str
    name: str
    status: Optional[str] = None
    leads_count: Optional[int] = 0
    created_time: Optional[str] = None
    privacy_policy_url: Optional[str] = None
    follow_up_action_url: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = []

    class Config:
        from_attributes = True


class FacebookSyncRequest(BaseModel):
    """Request to sync leads from Facebook"""
    form_id: str = Field(..., description="Facebook Lead Ad form ID")


class FacebookSyncResponse(BaseModel):
    """Response after syncing Facebook leads"""
    success: bool
    imported: int
    skipped: int
    errors: List[str]
    message: str


class FacebookLeadPreview(BaseModel):
    """Preview of Facebook Lead"""
    id: str
    created_time: str
    field_data: List[Dict[str, Any]]


class FacebookLeadPreviewResponse(BaseModel):
    """Response for lead preview"""
    form_id: str
    preview_count: int
    leads: List[FacebookLeadPreview]
