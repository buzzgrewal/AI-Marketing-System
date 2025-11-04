from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class AudienceType(str, enum.Enum):
    CUSTOM = "custom"
    LOOKALIKE = "lookalike"
    SAVED = "saved"


class AudiencePlatform(str, enum.Enum):
    META = "meta"  # Facebook/Instagram
    GOOGLE = "google"  # Google Ads
    BOTH = "both"


class AudienceStatus(str, enum.Enum):
    DRAFT = "draft"
    SYNCING = "syncing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class EventType(str, enum.Enum):
    PAGE_VIEW = "page_view"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    LEAD = "lead"
    SIGNUP = "signup"
    CUSTOM = "custom"


class RetargetingAudience(Base):
    """Retargeting audience for ad campaigns"""
    __tablename__ = "retargeting_audiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Audience details
    name = Column(String, nullable=False)
    description = Column(Text)
    audience_type = Column(String, default=AudienceType.CUSTOM)
    platform = Column(String, default=AudiencePlatform.META)
    status = Column(String, default=AudienceStatus.DRAFT)

    # Platform IDs
    meta_audience_id = Column(String)  # Facebook Custom Audience ID
    google_audience_id = Column(String)  # Google Ads Audience ID

    # Audience criteria
    criteria = Column(JSON)  # Rules for audience inclusion
    # Example: {
    #   "events": ["purchase", "add_to_cart"],
    #   "timeframe_days": 30,
    #   "exclude_purchasers": true,
    #   "min_actions": 1,
    #   "url_contains": "/products/"
    # }

    # Size tracking
    estimated_size = Column(Integer, default=0)
    actual_size = Column(Integer, default=0)
    last_sync_at = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    synced_at = Column(DateTime(timezone=True))

    # Error tracking
    error_message = Column(Text)
    sync_attempts = Column(Integer, default=0)

    # Relationships
    events = relationship("RetargetingEvent", back_populates="audience")
    campaigns = relationship("RetargetingCampaign", back_populates="audience")


class RetargetingEvent(Base):
    """Individual tracking event for retargeting"""
    __tablename__ = "retargeting_events"

    id = Column(Integer, primary_key=True, index=True)
    audience_id = Column(Integer, ForeignKey("retargeting_audiences.id"), nullable=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)

    # Event details
    event_type = Column(String, nullable=False)
    event_name = Column(String)
    platform = Column(String)  # meta, google, website

    # Event data
    event_data = Column(JSON)  # Additional event properties
    # Example: {
    #   "product_id": "123",
    #   "value": 49.99,
    #   "currency": "USD",
    #   "url": "/product/cycling-shoes"
    # }

    # Tracking
    user_identifier = Column(String)  # Email, phone, or hashed ID
    session_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(Text)

    # Conversion tracking
    conversion_value = Column(Float)
    currency = Column(String)

    # Timestamps
    event_time = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    audience = relationship("RetargetingAudience", back_populates="events")


class RetargetingCampaign(Base):
    """Retargeting ad campaign"""
    __tablename__ = "retargeting_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audience_id = Column(Integer, ForeignKey("retargeting_audiences.id"), nullable=False)

    # Campaign details
    name = Column(String, nullable=False)
    description = Column(Text)
    platform = Column(String, nullable=False)
    status = Column(String, default="draft")  # draft, active, paused, completed

    # Platform campaign IDs
    meta_campaign_id = Column(String)
    google_campaign_id = Column(String)

    # Campaign content
    ad_creative = Column(JSON)  # Ad copy, images, etc.
    budget_daily = Column(Float)
    budget_total = Column(Float)
    currency = Column(String, default="USD")

    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)

    # Calculated metrics
    ctr = Column(Float, default=0.0)  # Click-through rate
    cpc = Column(Float, default=0.0)  # Cost per click
    cpa = Column(Float, default=0.0)  # Cost per acquisition
    roas = Column(Float, default=0.0)  # Return on ad spend

    # Scheduling
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_synced_at = Column(DateTime(timezone=True))

    # Relationships
    audience = relationship("RetargetingAudience", back_populates="campaigns")


class RetargetingPerformance(Base):
    """Daily performance tracking for retargeting campaigns"""
    __tablename__ = "retargeting_performance"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("retargeting_campaigns.id"), nullable=False)

    # Date
    date = Column(DateTime(timezone=True), nullable=False)

    # Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)

    # Calculated
    ctr = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    cpa = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
