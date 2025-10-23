from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class LeadSource(str, enum.Enum):
    SHOPIFY = "shopify"
    MANUAL = "manual"
    IMPORT = "import"
    FACEBOOK = "facebook"
    WEBSITE = "website"
    EVENT = "event"
    OTHER = "other"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CUSTOMER = "customer"
    UNSUBSCRIBED = "unsubscribed"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    location = Column(String)

    # Consent tracking
    email_consent = Column(Boolean, default=False)
    sms_consent = Column(Boolean, default=False)
    consent_date = Column(DateTime(timezone=True))
    consent_source = Column(String)

    # Lead information
    source = Column(String, default=LeadSource.MANUAL)
    status = Column(String, default=LeadStatus.NEW)

    # Interests and segmentation
    interests = Column(Text)  # JSON stored as text
    sport_type = Column(String)  # cycling, triathlon, running
    customer_type = Column(String)  # athlete, coach, team, bike_fitter

    # Engagement tracking
    last_contact_date = Column(DateTime(timezone=True))
    engagement_score = Column(Integer, default=0)

    # Notes
    notes = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
