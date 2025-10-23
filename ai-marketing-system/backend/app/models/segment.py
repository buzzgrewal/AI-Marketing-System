from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class Segment(Base):
    """Lead segment model for advanced targeting"""
    
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Segment criteria stored as JSON
    # Format: {
    #   "operator": "AND" | "OR",
    #   "conditions": [
    #     {"field": "sport_type", "operator": "equals", "value": "cycling"},
    #     {"field": "status", "operator": "in", "value": ["new", "active"]},
    #     ...
    #   ]
    # }
    criteria = Column(JSON, nullable=False)
    
    # Segment type
    segment_type = Column(String(50), default="dynamic")  # dynamic, static
    
    # Statistics
    lead_count = Column(Integer, default=0)  # Cached count
    last_calculated = Column(DateTime, nullable=True)
    
    # Usage tracking
    campaign_count = Column(Integer, default=0)  # How many campaigns use this
    last_used = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Tags for organization
    tags = Column(JSON, nullable=True)  # ["high-value", "engaged", etc.]

    def __repr__(self):
        return f"<Segment(id={self.id}, name='{self.name}', lead_count={self.lead_count})>"

