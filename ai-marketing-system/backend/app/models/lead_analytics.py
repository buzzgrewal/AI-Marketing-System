"""
Lead Analytics Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class LeadAnalytics(Base):
    """Model for aggregated lead analytics data"""
    __tablename__ = "lead_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(100), nullable=False)  # e.g., 'website_form', 'google_ads', 'facebook'

    # Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    leads_generated = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)

    # Calculated metrics
    conversion_rate = Column(Float, default=0.0)  # leads/clicks
    cost_per_lead = Column(Float, default=0.0)  # cost/leads
    roi = Column(Float, default=0.0)  # (revenue-cost)/cost
    click_through_rate = Column(Float, default=0.0)  # clicks/impressions

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="lead_analytics")


class LeadSourcePerformance(Base):
    """Model for tracking individual lead source performance"""
    __tablename__ = "lead_source_performance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source = Column(String(100), nullable=False)
    source_id = Column(String(255))  # External ID from source (e.g., campaign ID)

    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Performance metrics
    total_leads = Column(Integer, default=0)
    qualified_leads = Column(Integer, default=0)
    converted_leads = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)

    # Quality metrics
    lead_quality_score = Column(Float, default=0.0)  # 0-100 score
    engagement_rate = Column(Float, default=0.0)  # % of leads that engaged
    response_rate = Column(Float, default=0.0)  # % of leads that responded

    # Additional data
    source_metadata = Column(JSON)  # Store any additional source-specific data

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="lead_source_performance")