from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class LeadBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    sport_type: Optional[str] = None
    customer_type: Optional[str] = None
    interests: Optional[str] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    email_consent: bool = False
    sms_consent: bool = False
    consent_source: Optional[str] = None
    source: str = "manual"


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    email_consent: Optional[bool] = None
    sms_consent: Optional[bool] = None
    status: Optional[str] = None
    sport_type: Optional[str] = None
    customer_type: Optional[str] = None
    interests: Optional[str] = None
    notes: Optional[str] = None


class LeadResponse(LeadBase):
    id: int
    email_consent: bool
    sms_consent: bool
    consent_date: Optional[datetime] = None
    consent_source: Optional[str] = None
    source: str
    status: str
    engagement_score: int
    last_contact_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadImportRequest(BaseModel):
    file_type: str  # csv, xlsx
    consent_confirmed: bool = False
    source: str = "import"
