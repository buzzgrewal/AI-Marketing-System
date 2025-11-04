from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


# Outreach Message Schemas

class OutreachMessageBase(BaseModel):
    lead_id: int
    outreach_type: str  # email, sms, linkedin
    subject: Optional[str] = None
    content: str
    scheduled_at: Optional[datetime] = None


class OutreachMessageCreate(OutreachMessageBase):
    sequence_id: Optional[int] = None
    personalization_data: Optional[Dict[str, Any]] = None


class OutreachMessageUpdate(BaseModel):
    subject: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class OutreachMessageResponse(OutreachMessageBase):
    id: int
    user_id: int
    sequence_id: Optional[int] = None
    status: str
    personalization_data: Optional[Dict[str, Any]] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    open_count: int
    click_count: int
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Outreach Sequence Schemas

class SequenceStepConfig(BaseModel):
    step: int
    delay_days: int
    type: str  # email, sms
    message_type: str  # intro, follow_up, promotional, re_engagement
    subject: Optional[str] = None
    template: Optional[str] = None
    context: Optional[str] = None


class OutreachSequenceBase(BaseModel):
    name: str
    description: Optional[str] = None
    sequence_steps: List[Dict[str, Any]]
    segment_id: Optional[int] = None
    target_filters: Optional[Dict[str, Any]] = None


class OutreachSequenceCreate(OutreachSequenceBase):
    stop_on_reply: bool = True
    max_retries: int = 3


class OutreachSequenceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    sequence_steps: Optional[List[Dict[str, Any]]] = None
    stop_on_reply: Optional[bool] = None


class OutreachSequenceResponse(OutreachSequenceBase):
    id: int
    user_id: int
    status: str
    total_enrolled: int
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_replied: int
    total_completed: int
    stop_on_reply: bool
    max_retries: int
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Enrollment Schemas

class EnrollmentCreate(BaseModel):
    sequence_id: int
    lead_ids: List[int]


class EnrollmentResponse(BaseModel):
    id: int
    sequence_id: int
    lead_id: int
    status: str
    current_step: int
    enrolled_at: datetime
    next_send_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    stop_reason: Optional[str] = None

    class Config:
        from_attributes = True


# Analytics Schemas

class SequenceAnalytics(BaseModel):
    sequence_id: int
    name: str
    status: str
    total_enrolled: int
    total_sent: int
    total_opened: int
    total_clicked: int
    total_replied: int
    total_completed: int
    open_rate: float
    click_rate: float
    reply_rate: float
    completion_rate: float
    enrollment_status: Dict[str, int]
    created_at: Optional[str] = None
    started_at: Optional[str] = None


class PersonalizedMessageRequest(BaseModel):
    lead_id: int
    message_type: str = "intro"
    template: Optional[str] = None
    additional_context: Optional[str] = None


class PersonalizedMessageResponse(BaseModel):
    subject: str
    body: str
    preview_text: str
    call_to_action: str
    personalization_tokens: Dict[str, str]
