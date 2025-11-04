# Import all models to register them with SQLAlchemy
from app.models.user import User
from app.models.lead import Lead
from app.models.campaign import Campaign, EmailLog
from app.models.content import GeneratedContent
from app.models.email_template import EmailTemplate
from app.models.scheduled_post import ScheduledPost
from app.models.segment import Segment
from app.models.ab_test import ABTest, ABTestVariant
from app.models.webhook import Webhook, WebhookEvent
from app.models.outreach import OutreachMessage, OutreachSequence, OutreachEnrollment
from app.models.retargeting import (
    RetargetingAudience, RetargetingEvent, RetargetingCampaign, RetargetingPerformance
)

__all__ = [
    "User", "Lead", "Campaign", "EmailLog", "GeneratedContent", "EmailTemplate",
    "ScheduledPost", "Segment", "ABTest", "ABTestVariant", "Webhook", "WebhookEvent",
    "OutreachMessage", "OutreachSequence", "OutreachEnrollment",
    "RetargetingAudience", "RetargetingEvent", "RetargetingCampaign", "RetargetingPerformance"
]
