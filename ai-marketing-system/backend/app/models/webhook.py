from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base


class Webhook(Base):
    """Webhook configuration for receiving events from external services"""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Webhook configuration
    provider = Column(String(100), nullable=False)  # sendgrid, mailchimp, facebook, twitter, etc.
    event_type = Column(String(100), nullable=False)  # email_open, email_click, email_bounce, post_engagement, etc.
    url_path = Column(String(255), unique=True, nullable=False)  # Unique path for this webhook
    
    # Security
    secret_key = Column(String(255), nullable=True)  # For webhook verification
    verify_signature = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_received_at = Column(DateTime, nullable=True)
    
    # Statistics
    total_events_received = Column(Integer, default=0)
    total_events_processed = Column(Integer, default=0)
    total_events_failed = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = relationship("WebhookEvent", back_populates="webhook", cascade="all, delete-orphan")


class WebhookEvent(Base):
    """Individual webhook event received"""
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)
    
    # Event details
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=False)  # Raw webhook payload
    
    # Processing
    status = Column(String(50), default="pending")  # pending, processed, failed
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Extracted information
    email = Column(String(255), nullable=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True, index=True)
    ab_test_variant_id = Column(Integer, ForeignKey("ab_test_variants.id"), nullable=True, index=True)
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=True)  # When the event occurred
    received_at = Column(DateTime, default=datetime.utcnow)  # When we received it
    
    # Relationships
    webhook = relationship("Webhook", back_populates="events")
    campaign = relationship("Campaign")
    lead = relationship("Lead")
    ab_test_variant = relationship("ABTestVariant")

