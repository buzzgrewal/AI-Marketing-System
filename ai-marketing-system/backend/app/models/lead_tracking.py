from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class LeadStage(str, enum.Enum):
    """Lead lifecycle stages"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    ENGAGED = "engaged"
    OPPORTUNITY = "opportunity"
    CUSTOMER = "customer"
    CHURNED = "churned"
    LOST = "lost"


class EngagementType(str, enum.Enum):
    """Types of engagement activities"""
    EMAIL_SENT = "email_sent"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    EMAIL_REPLIED = "email_replied"
    SMS_SENT = "sms_sent"
    SMS_REPLIED = "sms_replied"
    FORM_SUBMITTED = "form_submitted"
    PAGE_VIEWED = "page_viewed"
    LINK_CLICKED = "link_clicked"
    CALL_MADE = "call_made"
    MEETING_SCHEDULED = "meeting_scheduled"
    PURCHASE_MADE = "purchase_made"
    CONTENT_DOWNLOADED = "content_downloaded"
    SOCIAL_INTERACTION = "social_interaction"
    AD_CLICKED = "ad_clicked"


class AttributionModel(str, enum.Enum):
    """Attribution model types"""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    U_SHAPED = "u_shaped"
    W_SHAPED = "w_shaped"


class LeadLifecycle(Base):
    """Track lead progression through lifecycle stages"""
    __tablename__ = "lead_lifecycle"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    # Stage information
    stage = Column(String, nullable=False)
    previous_stage = Column(String)

    # Transition details
    entered_at = Column(DateTime(timezone=True), server_default=func.now())
    exited_at = Column(DateTime(timezone=True))
    duration_days = Column(Integer)  # Time spent in this stage

    # Reason for transition
    transition_reason = Column(Text)
    triggered_by = Column(String)  # campaign_id, user_id, automation_id, etc.

    # Stage metrics
    touchpoints_count = Column(Integer, default=0)  # Number of interactions in this stage
    engagement_score = Column(Integer, default=0)  # Engagement during this stage

    # Metadata
    is_current_stage = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Additional context
    notes = Column(Text)


class LeadScore(Base):
    """Lead scoring system with historical tracking"""
    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    # Score components (each 0-100)
    demographic_score = Column(Integer, default=0)  # Profile completeness, fit
    behavioral_score = Column(Integer, default=0)  # Engagement, activity
    firmographic_score = Column(Integer, default=0)  # Company/business fit
    engagement_score = Column(Integer, default=0)  # Recent interactions
    intent_score = Column(Integer, default=0)  # Purchase intent signals

    # Composite scores
    total_score = Column(Integer, default=0)  # Weighted total (0-100)
    previous_score = Column(Integer)  # Previous score for comparison

    # Score classification
    grade = Column(String)  # A+, A, B+, B, C+, C, D
    temperature = Column(String)  # hot, warm, cold

    # Scoring metadata
    score_factors = Column(JSON)  # Breakdown of what contributed to score
    last_calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    score_changed = Column(Boolean, default=False)
    score_change_amount = Column(Integer)  # +/- change from previous

    # Decay settings
    decay_rate = Column(Float, default=0.1)  # Score decay per day of inactivity
    last_activity_date = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EngagementHistory(Base):
    """Detailed log of all lead interactions"""
    __tablename__ = "engagement_history"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    # Engagement details
    engagement_type = Column(String, nullable=False)
    engagement_channel = Column(String)  # email, sms, web, social, phone, etc.

    # Source tracking
    source_type = Column(String)  # campaign, sequence, manual, automation
    source_id = Column(Integer)  # ID of campaign, sequence, etc.
    source_name = Column(String)  # Name for display

    # Engagement data
    title = Column(String)
    description = Column(Text)
    metadata = Column(JSON)  # Additional context

    # Value tracking
    engagement_value = Column(Integer, default=0)  # Relative value (0-100)
    revenue_attributed = Column(Float)  # Revenue attributed to this engagement

    # Timestamp
    engaged_at = Column(DateTime(timezone=True), server_default=func.now())

    # IP and device tracking
    ip_address = Column(String)
    user_agent = Column(Text)
    device_type = Column(String)  # desktop, mobile, tablet

    # Location
    location = Column(String)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LeadAttribution(Base):
    """Multi-touch attribution for lead conversions"""
    __tablename__ = "lead_attribution"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    # Conversion event
    conversion_type = Column(String, nullable=False)  # lead_created, qualified, opportunity, customer
    conversion_value = Column(Float)  # Revenue or value
    conversion_date = Column(DateTime(timezone=True), nullable=False)

    # Attribution model
    attribution_model = Column(String, default=AttributionModel.LINEAR)

    # Touchpoint tracking
    touchpoints = Column(JSON)  # Array of all touchpoints with attribution weight
    # Example: [
    #   {"type": "campaign", "id": 123, "name": "Email Campaign", "weight": 0.25, "date": "..."},
    #   {"type": "sequence", "id": 456, "name": "Outreach Seq", "weight": 0.50, "date": "..."},
    # ]

    # First touch attribution
    first_touch_source = Column(String)
    first_touch_id = Column(Integer)
    first_touch_name = Column(String)
    first_touch_date = Column(DateTime(timezone=True))
    first_touch_weight = Column(Float, default=0.0)

    # Last touch attribution
    last_touch_source = Column(String)
    last_touch_id = Column(Integer)
    last_touch_name = Column(String)
    last_touch_date = Column(DateTime(timezone=True))
    last_touch_weight = Column(Float, default=0.0)

    # Key touchpoints (most influential)
    primary_touchpoint = Column(JSON)  # Most influential touchpoint
    secondary_touchpoint = Column(JSON)  # Second most influential

    # Journey metrics
    total_touchpoints = Column(Integer, default=0)
    journey_duration_days = Column(Integer)  # Time from first touch to conversion
    avg_time_between_touches = Column(Float)  # Days

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LeadJourney(Base):
    """Complete lead journey visualization data"""
    __tablename__ = "lead_journeys"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, unique=True)

    # Journey timeline
    journey_start_date = Column(DateTime(timezone=True))
    last_activity_date = Column(DateTime(timezone=True))
    journey_duration_days = Column(Integer, default=0)

    # Journey stages
    current_stage = Column(String)
    stages_completed = Column(JSON)  # Array of completed stages with dates

    # Milestones
    milestones = Column(JSON)  # Key events in the journey
    # Example: [
    #   {"type": "first_contact", "date": "...", "source": "..."},
    #   {"type": "qualified", "date": "...", "score": 75},
    #   {"type": "opportunity", "date": "...", "value": 5000}
    # ]

    # Journey metrics
    total_engagements = Column(Integer, default=0)
    total_touchpoints = Column(Integer, default=0)
    email_engagements = Column(Integer, default=0)
    form_submissions = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    purchases = Column(Integer, default=0)

    # Journey health
    engagement_trend = Column(String)  # increasing, stable, declining
    days_since_last_activity = Column(Integer)
    risk_of_churn = Column(Float)  # 0.0 to 1.0

    # Journey path
    typical_path = Column(Boolean, default=True)  # Following typical conversion path
    path_deviation = Column(Text)  # How this lead's path differs

    # Revenue tracking
    lifetime_value = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    predicted_value = Column(Float)  # ML-predicted future value

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LeadActivitySummary(Base):
    """Daily/weekly aggregated activity summary for performance"""
    __tablename__ = "lead_activity_summary"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)

    # Time period
    period_type = Column(String, nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Activity counts
    emails_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)
    forms_submitted = Column(Integer, default=0)
    pages_viewed = Column(Integer, default=0)
    total_engagements = Column(Integer, default=0)

    # Scores
    period_engagement_score = Column(Integer, default=0)
    score_change = Column(Integer, default=0)  # Change from previous period

    # Status
    was_active = Column(Boolean, default=False)
    stage_at_start = Column(String)
    stage_at_end = Column(String)
    stage_changed = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
