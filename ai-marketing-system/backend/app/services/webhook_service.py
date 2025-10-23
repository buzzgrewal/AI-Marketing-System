import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.webhook import Webhook, WebhookEvent
from ..models.campaign import Campaign, EmailLog
from ..models.lead import Lead
from ..models.ab_test import ABTestVariant
from ..services import ab_test_service


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str,
    algorithm: str = "sha256"
) -> bool:
    """
    Verify webhook signature using HMAC
    """
    if not secret or not signature:
        return False
    
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False


def process_webhook_event(
    db: Session,
    webhook_event: WebhookEvent
) -> bool:
    """
    Process a webhook event and update relevant metrics
    
    Returns True if processing succeeded, False otherwise
    """
    try:
        event_data = webhook_event.event_data
        event_type = webhook_event.event_type.lower()
        
        # Extract email and IDs from event data
        email = event_data.get("email") or event_data.get("recipient")
        campaign_id = event_data.get("campaign_id")
        
        # Find lead by email
        lead = None
        if email:
            lead = db.query(Lead).filter(Lead.email == email).first()
            if lead:
                webhook_event.lead_id = lead.id
        
        # Find campaign
        campaign = None
        if campaign_id:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if campaign:
                webhook_event.campaign_id = campaign_id
        
        # Process based on event type
        if "open" in event_type or event_type == "opened":
            process_email_open(db, webhook_event, campaign, lead)
        elif "click" in event_type or event_type == "clicked":
            process_email_click(db, webhook_event, campaign, lead)
        elif "bounce" in event_type or event_type == "bounced":
            process_email_bounce(db, webhook_event, campaign, lead)
        elif "delivered" in event_type or event_type == "delivery":
            process_email_delivered(db, webhook_event, campaign, lead)
        elif "unsubscribe" in event_type or event_type == "unsubscribed":
            process_email_unsubscribe(db, webhook_event, campaign, lead)
        elif "spam" in event_type or "complaint" in event_type:
            process_spam_complaint(db, webhook_event, campaign, lead)
        else:
            # Unknown event type, mark as processed anyway
            pass
        
        # Mark as processed
        webhook_event.status = "processed"
        webhook_event.processed_at = datetime.utcnow()
        
        # Update webhook stats
        webhook = db.query(Webhook).filter(Webhook.id == webhook_event.webhook_id).first()
        if webhook:
            webhook.total_events_processed += 1
            webhook.last_received_at = datetime.utcnow()
        
        db.commit()
        return True
        
    except Exception as e:
        webhook_event.status = "failed"
        webhook_event.error_message = str(e)
        
        # Update webhook stats
        webhook = db.query(Webhook).filter(Webhook.id == webhook_event.webhook_id).first()
        if webhook:
            webhook.total_events_failed += 1
        
        db.commit()
        return False


def process_email_open(
    db: Session,
    event: WebhookEvent,
    campaign: Optional[Campaign],
    lead: Optional[Lead]
):
    """Process email open event"""
    if campaign:
        campaign.total_opened += 1
        
        # Update email log if exists
        if lead:
            email_log = db.query(EmailLog).filter(
                EmailLog.campaign_id == campaign.id,
                EmailLog.lead_id == lead.id,
                EmailLog.status != "opened"
            ).first()
            
            if email_log:
                email_log.status = "opened"
                email_log.opened_at = event.event_timestamp or datetime.utcnow()
    
    # Update A/B test variant if applicable
    variant_id = event.event_data.get("ab_test_variant_id")
    if variant_id:
        variant = db.query(ABTestVariant).filter(ABTestVariant.id == variant_id).first()
        if variant:
            variant.total_opened += 1
            ab_test_service.calculate_variant_metrics(variant)
            event.ab_test_variant_id = variant_id


def process_email_click(
    db: Session,
    event: WebhookEvent,
    campaign: Optional[Campaign],
    lead: Optional[Lead]
):
    """Process email click event"""
    if campaign:
        campaign.total_clicked += 1
        
        # Update email log if exists
        if lead:
            email_log = db.query(EmailLog).filter(
                EmailLog.campaign_id == campaign.id,
                EmailLog.lead_id == lead.id
            ).first()
            
            if email_log:
                email_log.status = "clicked"
                email_log.clicked_at = event.event_timestamp or datetime.utcnow()
    
    # Update A/B test variant if applicable
    variant_id = event.event_data.get("ab_test_variant_id")
    if variant_id:
        variant = db.query(ABTestVariant).filter(ABTestVariant.id == variant_id).first()
        if variant:
            variant.total_clicked += 1
            ab_test_service.calculate_variant_metrics(variant)
            event.ab_test_variant_id = variant_id


def process_email_bounce(
    db: Session,
    event: WebhookEvent,
    campaign: Optional[Campaign],
    lead: Optional[Lead]
):
    """Process email bounce event"""
    if lead:
        # Mark lead as bounced - may want to disable future emails
        lead.email_consent = False
    
    # Update email log if exists
    if campaign and lead:
        email_log = db.query(EmailLog).filter(
            EmailLog.campaign_id == campaign.id,
            EmailLog.lead_id == lead.id
        ).first()
        
        if email_log:
            email_log.status = "bounced"
            email_log.error_message = event.event_data.get("reason", "Email bounced")
    
    # Update A/B test variant if applicable
    variant_id = event.event_data.get("ab_test_variant_id")
    if variant_id:
        variant = db.query(ABTestVariant).filter(ABTestVariant.id == variant_id).first()
        if variant:
            variant.total_bounced += 1
            ab_test_service.calculate_variant_metrics(variant)
            event.ab_test_variant_id = variant_id


def process_email_delivered(
    db: Session,
    event: WebhookEvent,
    campaign: Optional[Campaign],
    lead: Optional[Lead]
):
    """Process email delivered event"""
    if campaign:
        campaign.total_delivered += 1
        
        # Update email log if exists
        if lead:
            email_log = db.query(EmailLog).filter(
                EmailLog.campaign_id == campaign.id,
                EmailLog.lead_id == lead.id
            ).first()
            
            if email_log:
                email_log.status = "delivered"
                email_log.delivered_at = event.event_timestamp or datetime.utcnow()
    
    # Update A/B test variant if applicable
    variant_id = event.event_data.get("ab_test_variant_id")
    if variant_id:
        variant = db.query(ABTestVariant).filter(ABTestVariant.id == variant_id).first()
        if variant:
            variant.total_delivered += 1
            ab_test_service.calculate_variant_metrics(variant)
            event.ab_test_variant_id = variant_id


def process_email_unsubscribe(
    db: Session,
    event: WebhookEvent,
    campaign: Optional[Campaign],
    lead: Optional[Lead]
):
    """Process unsubscribe event"""
    if lead:
        lead.email_consent = False
    
    if campaign:
        campaign.total_unsubscribed += 1
    
    # Update A/B test variant if applicable
    variant_id = event.event_data.get("ab_test_variant_id")
    if variant_id:
        variant = db.query(ABTestVariant).filter(ABTestVariant.id == variant_id).first()
        if variant:
            variant.total_unsubscribed += 1
            event.ab_test_variant_id = variant_id


def process_spam_complaint(
    db: Session,
    event: WebhookEvent,
    campaign: Optional[Campaign],
    lead: Optional[Lead]
):
    """Process spam complaint"""
    if lead:
        lead.email_consent = False
        # Optionally mark lead for special handling


def parse_sendgrid_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse SendGrid webhook event into standard format"""
    return {
        "email": payload.get("email"),
        "event_type": payload.get("event"),
        "timestamp": payload.get("timestamp"),
        "campaign_id": payload.get("campaign_id"),
        "url": payload.get("url"),  # For click events
        "reason": payload.get("reason"),  # For bounce events
    }


def parse_mailchimp_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Mailchimp webhook event into standard format"""
    event_type = payload.get("type")
    data = payload.get("data", {})
    
    return {
        "email": data.get("email"),
        "event_type": event_type,
        "timestamp": payload.get("fired_at"),
        "campaign_id": data.get("campaign_id"),
    }


def parse_generic_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Parse generic webhook event"""
    return {
        "email": payload.get("email"),
        "event_type": payload.get("event_type"),
        "timestamp": payload.get("timestamp"),
        "campaign_id": payload.get("campaign_id"),
        "ab_test_variant_id": payload.get("ab_test_variant_id"),
    }


def get_supported_providers() -> list:
    """Get list of supported webhook providers"""
    return [
        {
            "provider": "sendgrid",
            "supported_events": ["delivered", "open", "click", "bounce", "dropped", "spam_report", "unsubscribe"],
            "requires_signature": True,
            "signature_header": "X-Twilio-Email-Event-Webhook-Signature",
            "documentation_url": "https://docs.sendgrid.com/for-developers/tracking-events/event"
        },
        {
            "provider": "mailchimp",
            "supported_events": ["subscribe", "unsubscribe", "campaign", "cleaned", "upemail"],
            "requires_signature": False,
            "signature_header": None,
            "documentation_url": "https://mailchimp.com/developer/transactional/docs/webhooks/"
        },
        {
            "provider": "mailgun",
            "supported_events": ["delivered", "opened", "clicked", "bounced", "unsubscribed", "complained"],
            "requires_signature": True,
            "signature_header": "X-Mailgun-Signature",
            "documentation_url": "https://documentation.mailgun.com/en/latest/user_manual.html#webhooks"
        },
        {
            "provider": "generic",
            "supported_events": ["open", "click", "bounce", "delivered", "unsubscribe"],
            "requires_signature": False,
            "signature_header": None,
            "documentation_url": None
        }
    ]

