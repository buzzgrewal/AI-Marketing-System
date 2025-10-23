from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class EmailTemplateBase(BaseModel):
    """Base schema for email template"""
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(default="general", description="Template category: welcome, promotional, newsletter, transactional, general")
    subject: str = Field(..., min_length=1, max_length=500, description="Email subject line")
    html_content: str = Field(..., min_length=1, description="HTML content of the email")
    plain_text_content: Optional[str] = Field(None, description="Plain text version")
    available_variables: Optional[str] = Field(None, description="JSON string of available variables")
    is_active: bool = Field(default=True, description="Whether template is active")
    is_default: bool = Field(default=False, description="Whether this is the default template for its category")


class EmailTemplateCreate(EmailTemplateBase):
    """Schema for creating a new email template"""
    pass


class EmailTemplateUpdate(BaseModel):
    """Schema for updating an email template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    html_content: Optional[str] = Field(None, min_length=1)
    plain_text_content: Optional[str] = None
    available_variables: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class EmailTemplateResponse(EmailTemplateBase):
    """Schema for email template response"""
    id: int
    usage_count: int
    last_used_at: Optional[datetime]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateRenderRequest(BaseModel):
    """Schema for rendering a template with variables"""
    template_id: int
    variables: Dict[str, Any] = Field(default_factory=dict, description="Variables to substitute in template")


class TemplateRenderResponse(BaseModel):
    """Schema for rendered template response"""
    subject: str
    html_content: str
    plain_text_content: Optional[str]

