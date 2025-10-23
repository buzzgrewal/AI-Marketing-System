from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class ScheduledPostBase(BaseModel):
    """Base schema for scheduled post"""
    platform: str = Field(..., description="Social media platform: facebook, instagram, twitter, linkedin")
    post_text: str = Field(..., min_length=1, description="Text content of the post")
    image_url: Optional[str] = Field(None, description="URL to image for the post")
    hashtags: Optional[str] = Field(None, description="Hashtags for the post")
    scheduled_time: datetime = Field(..., description="When to post (future datetime)")
    timezone: str = Field(default="UTC", description="Timezone for scheduled time")
    auto_post: bool = Field(default=True, description="Whether to auto-post or require manual approval")
    platform_settings: Optional[Dict[str, Any]] = Field(None, description="Platform-specific settings")
    content_id: Optional[int] = Field(None, description="Link to generated content")

    @validator('platform')
    def validate_platform(cls, v):
        allowed = ['facebook', 'instagram', 'twitter', 'linkedin']
        if v.lower() not in allowed:
            raise ValueError(f'Platform must be one of: {", ".join(allowed)}')
        return v.lower()

    @validator('scheduled_time')
    def validate_future_time(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v


class ScheduledPostCreate(ScheduledPostBase):
    """Schema for creating a scheduled post"""
    pass


class ScheduledPostUpdate(BaseModel):
    """Schema for updating a scheduled post"""
    platform: Optional[str] = None
    post_text: Optional[str] = None
    image_url: Optional[str] = None
    hashtags: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    timezone: Optional[str] = None
    auto_post: Optional[bool] = None
    status: Optional[str] = None
    platform_settings: Optional[Dict[str, Any]] = None


class ScheduledPostResponse(ScheduledPostBase):
    """Schema for scheduled post response"""
    id: int
    status: str
    posted_at: Optional[datetime]
    platform_post_id: Optional[str]
    platform_url: Optional[str]
    error_message: Optional[str]
    likes_count: int
    comments_count: int
    shares_count: int
    reach: int
    engagement_rate: int
    metrics_last_updated: Optional[datetime]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SchedulingCalendarResponse(BaseModel):
    """Schema for calendar view of scheduled posts"""
    date: str
    posts: list[ScheduledPostResponse]


class PostMetricsUpdate(BaseModel):
    """Schema for updating post metrics"""
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    shares_count: Optional[int] = 0
    reach: Optional[int] = 0


class BulkScheduleRequest(BaseModel):
    """Schema for bulk scheduling posts"""
    posts: list[ScheduledPostCreate]


class ScheduleFromContentRequest(BaseModel):
    """Schema for scheduling from existing content"""
    content_id: int
    scheduled_time: datetime
    timezone: str = "UTC"
    auto_post: bool = True
    platform_settings: Optional[Dict[str, Any]] = None

