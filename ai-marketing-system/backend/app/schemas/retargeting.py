from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


# Audience Schemas

class AudienceBase(BaseModel):
    name: str
    description: Optional[str] = None
    audience_type: str = "custom"
    platform: str = "meta"
    criteria: Optional[Dict[str, Any]] = None


class AudienceCreate(AudienceBase):
    pass


class AudienceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None


class AudienceResponse(AudienceBase):
    id: int
    user_id: int
    status: str
    meta_audience_id: Optional[str] = None
    google_audience_id: Optional[str] = None
    estimated_size: int
    actual_size: int
    last_sync_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# Event Schemas

class EventCreate(BaseModel):
    event_type: str
    event_name: Optional[str] = None
    platform: str
    event_data: Optional[Dict[str, Any]] = None
    user_identifier: Optional[str] = None
    session_id: Optional[str] = None
    conversion_value: Optional[float] = None
    currency: Optional[str] = "USD"


class EventResponse(BaseModel):
    id: int
    audience_id: Optional[int] = None
    lead_id: Optional[int] = None
    event_type: str
    event_name: Optional[str] = None
    platform: str
    event_data: Optional[Dict[str, Any]] = None
    user_identifier: Optional[str] = None
    conversion_value: Optional[float] = None
    event_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Campaign Schemas

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    audience_id: int
    platform: str
    ad_creative: Optional[Dict[str, Any]] = None
    budget_daily: Optional[float] = None
    budget_total: Optional[float] = None
    currency: str = "USD"


class CampaignCreate(CampaignBase):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    budget_daily: Optional[float] = None
    budget_total: Optional[float] = None
    ad_creative: Optional[Dict[str, Any]] = None


class CampaignResponse(CampaignBase):
    id: int
    user_id: int
    status: str
    meta_campaign_id: Optional[str] = None
    google_campaign_id: Optional[str] = None
    impressions: int
    clicks: int
    conversions: int
    spend: float
    revenue: float
    ctr: float
    cpc: float
    cpa: float
    roas: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Analytics Schemas

class AudienceAnalytics(BaseModel):
    audience_id: int
    name: str
    platform: str
    total_size: int
    total_events: int
    events_by_type: Dict[str, int]
    top_conversions: List[Dict[str, Any]]


class CampaignAnalytics(BaseModel):
    campaign_id: int
    name: str
    platform: str
    total_impressions: int
    total_clicks: int
    total_conversions: int
    total_spend: float
    total_revenue: float
    avg_ctr: float
    avg_cpc: float
    avg_cpa: float
    avg_roas: float
    daily_performance: List[Dict[str, Any]]
