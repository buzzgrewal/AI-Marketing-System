from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    campaign_type: str  # email, sms, social
    subject: Optional[str] = None
    content: Optional[str] = None
    template_id: Optional[int] = None  # Optional template to use
    segment_id: Optional[int] = None  # Optional segment to target
    target_segment: Optional[str] = None
    target_sport_type: Optional[str] = None


class CampaignCreate(CampaignBase):
    scheduled_date: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    template_id: Optional[int] = None
    segment_id: Optional[int] = None
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None


class CampaignResponse(CampaignBase):
    id: int
    status: str
    total_recipients: int
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int
    scheduled_date: Optional[datetime] = None
    sent_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignStats(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_sent: int
    avg_open_rate: float
    avg_click_rate: float
    avg_conversion_rate: float
