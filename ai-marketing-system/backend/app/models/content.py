from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Float
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class ContentType(str, enum.Enum):
    SOCIAL_POST = "social_post"
    EMAIL_TEMPLATE = "email_template"
    AD_COPY = "ad_copy"
    BLOG_POST = "blog_post"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    POSTED = "posted"
    ARCHIVED = "archived"


class Platform(str, enum.Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    EMAIL = "email"


class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String, nullable=False)
    platform = Column(String)

    # Content details
    title = Column(String)
    caption = Column(Text)
    body = Column(Text)
    hashtags = Column(String)

    # Image/Media
    image_url = Column(String)
    image_prompt = Column(Text)
    media_type = Column(String)

    # AI Generation details
    prompt_used = Column(Text)
    ai_model = Column(String)

    # Status and approval
    status = Column(String, default=ContentStatus.DRAFT)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))

    # Performance tracking (after manual posting)
    posted_at = Column(DateTime(timezone=True))
    platform_post_id = Column(String)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContentTemplate(Base):
    __tablename__ = "content_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    template_text = Column(Text, nullable=False)
    variables = Column(Text)  # JSON list of variables
    description = Column(Text)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
