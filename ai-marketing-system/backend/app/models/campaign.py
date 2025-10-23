from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class CampaignType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    SOCIAL = "social"


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    campaign_type = Column(String, nullable=False)
    status = Column(String, default=CampaignStatus.DRAFT)

    # Campaign content
    subject = Column(String)  # For emails
    content = Column(Text)
    template_id = Column(Integer)

    # Targeting
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=True)  # Link to segment
    target_segment = Column(String)  # JSON stored as text (legacy)
    target_sport_type = Column(String)

    # Scheduling
    scheduled_date = Column(DateTime(timezone=True))
    sent_date = Column(DateTime(timezone=True))

    # Statistics
    total_recipients = Column(Integer, default=0)
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    total_unsubscribed = Column(Integer, default=0)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ab_tests = relationship("ABTest", back_populates="campaign")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    lead_id = Column(Integer, ForeignKey("leads.id"))

    # Email details
    recipient_email = Column(String, nullable=False)
    subject = Column(String)

    # Status
    status = Column(String)  # sent, delivered, opened, clicked, bounced, failed
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))

    # Error tracking
    error_message = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
