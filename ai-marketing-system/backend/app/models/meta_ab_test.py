"""
Meta (Facebook/Instagram) A/B Testing Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class MetaPlatform(str, enum.Enum):
    """Platforms for Meta A/B testing"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    BOTH = "both"


class MetaTestType(str, enum.Enum):
    """Types of Meta A/B tests"""
    AD_CREATIVE = "ad_creative"
    AUDIENCE = "audience"
    PLACEMENT = "placement"
    BUDGET = "budget"
    BIDDING = "bidding"


class MetaTestStatus(str, enum.Enum):
    """Status of Meta A/B test"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class MetaABTest(Base):
    """Model for Meta (Facebook/Instagram) A/B tests"""
    __tablename__ = "meta_ab_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Meta-specific fields
    campaign_id = Column(String(255))  # Facebook Campaign ID
    ad_account_id = Column(String(255), nullable=False)  # Facebook Ad Account ID
    platform = Column(Enum(MetaPlatform), default=MetaPlatform.BOTH)
    test_type = Column(Enum(MetaTestType), nullable=False)

    # Test configuration
    budget_per_variant = Column(Float, default=50.0)  # Daily budget per variant
    duration_days = Column(Integer, default=7)
    target_audience = Column(JSON)  # Audience targeting criteria
    success_metric = Column(String(100))  # e.g., 'cost_per_result', 'cpm', 'ctr', 'conversions'

    # Status and timing
    status = Column(Enum(MetaTestStatus), default=MetaTestStatus.DRAFT)
    scheduled_start = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))

    # Results
    winner_variant_id = Column(Integer, ForeignKey("meta_ab_test_variants.id"))
    confidence_level = Column(Float)  # Statistical confidence

    # Metadata
    meta_experiment_id = Column(String(255))  # Facebook Experiment ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="meta_ab_tests")
    variants = relationship("MetaABTestVariant", back_populates="test", cascade="all, delete-orphan", foreign_keys="MetaABTestVariant.test_id")
    winner_variant = relationship("MetaABTestVariant", foreign_keys=[winner_variant_id], post_update=True)


class MetaABTestVariant(Base):
    """Model for Meta A/B test variants"""
    __tablename__ = "meta_ab_test_variants"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("meta_ab_tests.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Creative content
    ad_creative = Column(JSON)  # Stores ad creative details
    headline = Column(String(255))
    primary_text = Column(Text)
    description_text = Column(Text)
    call_to_action = Column(String(100))
    link_url = Column(String(500))

    # Media
    image_url = Column(String(500))
    video_url = Column(String(500))
    carousel_items = Column(JSON)  # For carousel ads

    # Targeting (if variant tests different audiences)
    audience_override = Column(JSON)
    placement_override = Column(JSON)

    # Budget/bidding (if variant tests different strategies)
    budget_override = Column(Float)
    bid_strategy_override = Column(String(50))

    # Performance metrics (populated from Facebook API)
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    cpm = Column(Float, default=0.0)  # Cost per 1000 impressions
    cpc = Column(Float, default=0.0)  # Cost per click
    ctr = Column(Float, default=0.0)  # Click-through rate
    conversion_rate = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)  # Return on ad spend

    # Meta-specific IDs
    ad_set_id = Column(String(255))  # Facebook Ad Set ID
    ad_id = Column(String(255))  # Facebook Ad ID

    # Status
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    test = relationship("MetaABTest", back_populates="variants", foreign_keys=[test_id])


class MetaABTestResult(Base):
    """Model for storing detailed Meta A/B test results"""
    __tablename__ = "meta_ab_test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("meta_ab_tests.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("meta_ab_test_variants.id"), nullable=False)

    # Time-series data
    date = Column(DateTime(timezone=True), nullable=False)
    hour = Column(Integer)  # 0-23 for hourly data

    # Metrics snapshot
    impressions = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)

    # Calculated metrics
    cpm = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)

    # Demographic breakdown (optional)
    demographic_data = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    test = relationship("MetaABTest")
    variant = relationship("MetaABTestVariant")