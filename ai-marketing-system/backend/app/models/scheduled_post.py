from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ScheduledPost(Base):
    """Scheduled social media post model"""
    
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Content reference
    content_id = Column(Integer, ForeignKey("generated_content.id"), nullable=True)
    
    # Post details
    platform = Column(String(50), nullable=False, index=True)  # facebook, instagram, twitter, linkedin
    post_text = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    hashtags = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_time = Column(DateTime, nullable=False, index=True)
    timezone = Column(String(50), default="UTC")
    
    # Status tracking
    status = Column(String(50), default="scheduled", index=True)  # scheduled, posting, posted, failed, cancelled
    posted_at = Column(DateTime, nullable=True)
    
    # Platform response
    platform_post_id = Column(String(200), nullable=True)  # ID from social media platform
    platform_url = Column(String(500), nullable=True)  # URL to the post
    error_message = Column(Text, nullable=True)
    
    # Engagement metrics (fetched after posting)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement_rate = Column(Integer, default=0)
    metrics_last_updated = Column(DateTime, nullable=True)
    
    # Auto-post settings
    auto_post = Column(Boolean, default=True)  # Whether to auto-post or manual approval
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Additional platform-specific settings
    platform_settings = Column(JSON, nullable=True)  # Store platform-specific options

    def __repr__(self):
        return f"<ScheduledPost(id={self.id}, platform='{self.platform}', status='{self.status}', scheduled_time='{self.scheduled_time}')>"

