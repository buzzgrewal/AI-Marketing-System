from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db.base import Base


class ABTest(Base):
    """A/B Test model for campaign optimization"""
    __tablename__ = "ab_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    
    # Test configuration
    test_type = Column(String(50), default="subject_line")  # subject_line, content, template, sender_name
    sample_size_percentage = Column(Float, default=20.0)  # Percentage of leads to include in test
    success_metric = Column(String(50), default="open_rate")  # open_rate, click_rate, conversion_rate
    
    # Test status
    status = Column(String(50), default="draft")  # draft, running, completed, cancelled
    winner_variant_id = Column(Integer, ForeignKey("ab_test_variants.id"), nullable=True)
    auto_select_winner = Column(Boolean, default=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="ab_tests")
    variants = relationship("ABTestVariant", back_populates="ab_test", foreign_keys="ABTestVariant.ab_test_id")
    winner_variant = relationship("ABTestVariant", foreign_keys=[winner_variant_id], post_update=True)


class ABTestVariant(Base):
    """Individual variant in an A/B test"""
    __tablename__ = "ab_test_variants"

    id = Column(Integer, primary_key=True, index=True)
    ab_test_id = Column(Integer, ForeignKey("ab_tests.id"), nullable=False)
    
    # Variant details
    name = Column(String(255), nullable=False)  # e.g., "Variant A", "Variant B"
    description = Column(Text, nullable=True)
    
    # Email content
    subject = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    sender_name = Column(String(255), nullable=True)
    
    # Test results
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    total_bounced = Column(Integer, default=0)
    total_unsubscribed = Column(Integer, default=0)
    
    # Calculated metrics
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    
    # Winner flag
    is_winner = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ab_test = relationship("ABTest", back_populates="variants", foreign_keys=[ab_test_id])
    template = relationship("EmailTemplate")

