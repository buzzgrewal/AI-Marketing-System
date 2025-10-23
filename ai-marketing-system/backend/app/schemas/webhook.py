from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Webhook Schemas
class WebhookBase(BaseModel):
    name: str = Field(..., description="Webhook name")
    description: Optional[str] = None
    provider: str = Field(..., description="Service provider (sendgrid, mailchimp, etc.)")
    event_type: str = Field(..., description="Type of event to track")
    verify_signature: bool = Field(default=True, description="Verify webhook signatures")
    is_active: bool = Field(default=True, description="Enable/disable webhook")


class WebhookCreate(WebhookBase):
    secret_key: Optional[str] = Field(None, description="Secret key for signature verification")


class WebhookUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    secret_key: Optional[str] = None
    verify_signature: Optional[bool] = None
    is_active: Optional[bool] = None


class WebhookResponse(WebhookBase):
    id: int
    url_path: str
    secret_key: Optional[str] = None
    last_received_at: Optional[datetime] = None
    total_events_received: int
    total_events_processed: int
    total_events_failed: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookWithURL(WebhookResponse):
    """Webhook response with full webhook URL"""
    webhook_url: str


# Webhook Event Schemas
class WebhookEventBase(BaseModel):
    event_type: str
    event_data: Dict[str, Any]
    event_timestamp: Optional[datetime] = None


class WebhookEventCreate(WebhookEventBase):
    webhook_id: int


class WebhookEventResponse(WebhookEventBase):
    id: int
    webhook_id: int
    status: str
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    email: Optional[str] = None
    campaign_id: Optional[int] = None
    lead_id: Optional[int] = None
    ab_test_variant_id: Optional[int] = None
    received_at: datetime

    class Config:
        from_attributes = True


# Webhook Event Processing
class ProcessEventRequest(BaseModel):
    """Request to manually process a webhook event"""
    event_id: int


class WebhookStats(BaseModel):
    """Webhook statistics"""
    total_webhooks: int = 0
    active_webhooks: int = 0
    total_events_received: int = 0
    total_events_processed: int = 0
    total_events_failed: int = 0
    events_by_type: Dict[str, int] = {}
    recent_events: List[WebhookEventResponse] = []


# Provider-specific event formats
class SendGridEvent(BaseModel):
    """SendGrid webhook event format"""
    email: str
    timestamp: int
    event: str  # delivered, open, click, bounce, etc.
    campaign_id: Optional[str] = None
    sg_message_id: Optional[str] = None
    url: Optional[str] = None  # For click events


class MailchimpEvent(BaseModel):
    """Mailchimp webhook event format"""
    type: str  # subscribe, unsubscribe, campaign
    fired_at: str
    data: Dict[str, Any]


class GenericWebhookPayload(BaseModel):
    """Generic webhook payload for testing"""
    event_type: str
    email: Optional[str] = None
    campaign_id: Optional[int] = None
    timestamp: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class WebhookTestRequest(BaseModel):
    """Request to test a webhook"""
    payload: Dict[str, Any]


class WebhookProviderInfo(BaseModel):
    """Information about supported webhook providers"""
    provider: str
    supported_events: List[str]
    requires_signature: bool
    signature_header: Optional[str] = None
    documentation_url: Optional[str] = None

