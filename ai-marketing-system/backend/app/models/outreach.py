from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class OutreachType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    LINKEDIN = "linkedin"


class OutreachStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"
    FAILED = "failed"


class SequenceStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DRAFT = "draft"


class OutreachMessage(Base):
    """Individual outreach message to a lead"""
    __tablename__ = "outreach_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    sequence_id = Column(Integer, ForeignKey("outreach_sequences.id"), nullable=True)

    # Message details
    outreach_type = Column(String, default=OutreachType.EMAIL)
    subject = Column(String)  # For emails
    content = Column(Text, nullable=False)

    # Personalization data
    personalization_data = Column(JSON)  # Stores variables used for personalization

    # Status tracking
    status = Column(String, default=OutreachStatus.DRAFT)
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    replied_at = Column(DateTime(timezone=True))

    # Engagement tracking
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    reply_text = Column(Text)

    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sequence = relationship("OutreachSequence", back_populates="messages")


class OutreachSequence(Base):
    """Email/message sequence automation"""
    __tablename__ = "outreach_sequences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Sequence details
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default=SequenceStatus.DRAFT)

    # Sequence configuration
    sequence_steps = Column(JSON)  # Array of step configurations
    # Example: [
    #   {"step": 1, "delay_days": 0, "type": "email", "subject": "...", "template": "..."},
    #   {"step": 2, "delay_days": 3, "type": "email", "subject": "...", "template": "..."}
    # ]

    # Targeting
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=True)
    target_filters = Column(JSON)  # Additional filtering criteria

    # Statistics
    total_enrolled = Column(Integer, default=0)
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_replied = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)

    # Settings
    stop_on_reply = Column(Boolean, default=True)  # Stop sequence if lead replies
    max_retries = Column(Integer, default=3)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    messages = relationship("OutreachMessage", back_populates="sequence")


class OutreachEnrollment(Base):
    """Tracks which leads are enrolled in which sequences"""
    __tablename__ = "outreach_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    sequence_id = Column(Integer, ForeignKey("outreach_sequences.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    # Status
    status = Column(String, default="active")  # active, completed, stopped, failed
    current_step = Column(Integer, default=0)

    # Timestamps
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    stopped_at = Column(DateTime(timezone=True))

    # Next action
    next_send_at = Column(DateTime(timezone=True))

    # Metadata
    stop_reason = Column(String)  # replied, unsubscribed, bounced, manual
