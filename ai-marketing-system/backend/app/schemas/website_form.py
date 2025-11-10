"""
Website Form Schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class FormField(BaseModel):
    """Schema for individual form field"""
    id: str
    label: str
    type: str  # text, email, tel, select, textarea, checkbox, radio
    required: bool = False
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None  # For select, radio, checkbox
    validation: Optional[Dict[str, Any]] = None  # Additional validation rules


class WebsiteFormBase(BaseModel):
    """Base schema for website form"""
    name: str
    description: Optional[str] = None
    fields: List[FormField]
    submit_text: str = "Submit"
    success_message: str = "Thank you for your submission!"


class WebsiteFormCreate(WebsiteFormBase):
    """Schema for creating a website form"""
    pass


class WebsiteFormUpdate(BaseModel):
    """Schema for updating a website form"""
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[FormField]] = None
    submit_text: Optional[str] = None
    success_message: Optional[str] = None
    is_active: Optional[bool] = None


class WebsiteFormResponse(WebsiteFormBase):
    """Schema for website form response"""
    id: int
    user_id: int
    is_active: bool
    embed_code: Optional[str] = None
    submission_count: int
    conversion_rate: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FormSubmissionCreate(BaseModel):
    """Schema for creating a form submission"""
    form_id: int
    data: Dict[str, Any]
    source_url: Optional[str] = None


class FormSubmissionResponse(BaseModel):
    """Schema for form submission response"""
    id: int
    form_id: int
    data: Dict[str, Any]
    source_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FormStats(BaseModel):
    """Schema for form statistics"""
    form_id: int
    form_name: str
    total_submissions: int
    conversion_rate: float
    submissions_today: int
    submissions_week: int
    submissions_month: int
    top_sources: List[Dict[str, Any]]