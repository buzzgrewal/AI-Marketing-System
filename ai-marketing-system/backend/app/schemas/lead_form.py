"""
Lead Form Schemas

Pydantic models for website form builder API.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class FormField(BaseModel):
    """Individual form field definition"""
    name: str = Field(..., description="Field identifier (e.g., 'email', 'first_name')")
    type: str = Field(..., description="Field type (text, email, tel, textarea, select, checkbox)")
    label: str = Field(..., description="Display label")
    required: bool = Field(default=False)
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None  # For select fields
    validation: Optional[str] = None  # Regex pattern for validation

    @validator('type')
    def validate_field_type(cls, v):
        allowed_types = ['text', 'email', 'tel', 'textarea', 'select', 'checkbox', 'radio', 'number', 'url']
        if v not in allowed_types:
            raise ValueError(f'Field type must be one of: {", ".join(allowed_types)}')
        return v


class FormCreate(BaseModel):
    """Schema for creating a new form"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    submit_button_text: str = "Submit"
    success_message: str = "Thank you! We'll be in touch soon."
    fields: List[FormField]
    theme_color: str = "#2563eb"
    background_color: str = "#ffffff"
    text_color: str = "#111827"
    redirect_url: Optional[str] = None
    enable_double_optin: bool = False
    require_consent: bool = True
    consent_text: str = "I agree to receive marketing communications"
    enable_recaptcha: bool = False
    enable_honeypot: bool = True
    rate_limit_enabled: bool = True
    max_submissions_per_ip: int = 5


class FormUpdate(BaseModel):
    """Schema for updating a form"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    submit_button_text: Optional[str] = None
    success_message: Optional[str] = None
    fields: Optional[List[FormField]] = None
    theme_color: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    redirect_url: Optional[str] = None
    enable_double_optin: Optional[bool] = None
    require_consent: Optional[bool] = None
    consent_text: Optional[str] = None
    enable_recaptcha: Optional[bool] = None
    enable_honeypot: Optional[bool] = None
    rate_limit_enabled: Optional[bool] = None
    max_submissions_per_ip: Optional[int] = None
    is_active: Optional[bool] = None


class FormResponse(BaseModel):
    """Schema for form response"""
    id: int
    name: str
    slug: str
    title: str
    description: Optional[str]
    submit_button_text: str
    success_message: str
    fields: List[Dict[str, Any]]
    theme_color: str
    background_color: str
    text_color: str
    redirect_url: Optional[str]
    enable_double_optin: bool
    require_consent: bool
    consent_text: str
    enable_recaptcha: bool
    enable_honeypot: bool
    rate_limit_enabled: bool
    max_submissions_per_ip: int
    is_active: bool
    submission_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FormSubmissionData(BaseModel):
    """Schema for public form submission"""
    data: Dict[str, Any] = Field(..., description="Form field values")
    honeypot: Optional[str] = Field(None, description="Hidden field for spam detection")


class FormSubmissionResponse(BaseModel):
    """Response after form submission"""
    success: bool
    message: str
    lead_id: Optional[int] = None
    redirect_url: Optional[str] = None


class FormStatsResponse(BaseModel):
    """Form statistics"""
    total_submissions: int
    pending_submissions: int
    processed_submissions: int
    spam_submissions: int
    conversion_rate: float
    recent_submissions: List[Dict[str, Any]]
