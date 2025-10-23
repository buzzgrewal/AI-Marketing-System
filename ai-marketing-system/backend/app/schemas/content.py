from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ContentGenerationRequest(BaseModel):
    content_type: str  # social_post, email_template, ad_copy
    platform: Optional[str] = None
    topic: str
    tone: str = "professional"  # professional, casual, friendly, enthusiastic
    target_audience: str = "cyclists and triathletes"
    additional_context: Optional[str] = None
    include_image: bool = False
    image_style: Optional[str] = "professional product photography"
    product_image_base64: Optional[str] = None  # User's product image to enhance/edit


class ContentResponse(BaseModel):
    id: int
    content_type: str
    platform: Optional[str] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    body: Optional[str] = None
    hashtags: Optional[str] = None
    image_url: Optional[str] = None
    image_prompt: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ContentUpdateRequest(BaseModel):
    title: Optional[str] = None
    caption: Optional[str] = None
    body: Optional[str] = None
    hashtags: Optional[str] = None
    status: Optional[str] = None


class ContentPerformanceUpdate(BaseModel):
    platform_post_id: str
    likes_count: Optional[int] = 0
    comments_count: Optional[int] = 0
    shares_count: Optional[int] = 0
    reach: Optional[int] = 0
