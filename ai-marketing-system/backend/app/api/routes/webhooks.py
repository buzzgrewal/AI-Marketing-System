from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, Header
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import json

from ...db.session import get_db
from ...models.webhook import Webhook, WebhookEvent
from ...schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookWithURL,
    WebhookEventResponse,
    WebhookStats,
    WebhookTestRequest,
    WebhookProviderInfo,
    ProcessEventRequest
)
from ...services import webhook_service
from ...core.config import settings

router = APIRouter()


@router.post("/", response_model=WebhookWithURL, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new webhook"""
    
    # Generate unique URL path
    unique_path = f"/webhooks/receive/{secrets.token_urlsafe(16)}"
    
    # Create webhook
    webhook = Webhook(
        name=webhook_data.name,
        description=webhook_data.description,
        provider=webhook_data.provider,
        event_type=webhook_data.event_type,
        url_path=unique_path,
        secret_key=webhook_data.secret_key or secrets.token_urlsafe(32),
        verify_signature=webhook_data.verify_signature,
        is_active=webhook_data.is_active
    )
    
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    
    # Build full webhook URL
    base_url = str(request.base_url).rstrip('/')
    webhook_url = f"{base_url}/api{unique_path}"
    
    response_data = webhook.__dict__.copy()
    response_data["webhook_url"] = webhook_url
    
    return response_data


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    is_active: Optional[bool] = None,
    provider: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all webhooks with optional filters"""
    query = db.query(Webhook)
    
    if is_active is not None:
        query = query.filter(Webhook.is_active == is_active)
    
    if provider:
        query = query.filter(Webhook.provider == provider)
    
    webhooks = query.order_by(Webhook.created_at.desc()).offset(skip).limit(limit).all()
    return webhooks


@router.get("/stats", response_model=WebhookStats)
async def get_webhook_stats(db: Session = Depends(get_db)):
    """Get webhook statistics"""
    total_webhooks = db.query(Webhook).count()
    active_webhooks = db.query(Webhook).filter(Webhook.is_active == True).count()
    
    # Aggregate event stats
    all_webhooks = db.query(Webhook).all()
    total_received = sum(w.total_events_received for w in all_webhooks)
    total_processed = sum(w.total_events_processed for w in all_webhooks)
    total_failed = sum(w.total_events_failed for w in all_webhooks)
    
    # Events by type
    events_by_type = {}
    event_types = db.query(WebhookEvent.event_type).distinct().all()
    for (event_type,) in event_types:
        count = db.query(WebhookEvent).filter(WebhookEvent.event_type == event_type).count()
        events_by_type[event_type] = count
    
    # Recent events (last 10)
    recent_events = db.query(WebhookEvent).order_by(
        WebhookEvent.received_at.desc()
    ).limit(10).all()
    
    return {
        "total_webhooks": total_webhooks,
        "active_webhooks": active_webhooks,
        "total_events_received": total_received,
        "total_events_processed": total_processed,
        "total_events_failed": total_failed,
        "events_by_type": events_by_type,
        "recent_events": recent_events
    }


@router.get("/providers", response_model=List[WebhookProviderInfo])
async def list_supported_providers():
    """List supported webhook providers"""
    providers = webhook_service.get_supported_providers()
    return providers


@router.get("/{webhook_id}", response_model=WebhookWithURL)
async def get_webhook(
    webhook_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Build full webhook URL
    base_url = str(request.base_url).rstrip('/')
    webhook_url = f"{base_url}/api{webhook.url_path}"
    
    response_data = webhook.__dict__.copy()
    response_data["webhook_url"] = webhook_url
    
    return response_data


@router.put("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: int,
    webhook_data: WebhookUpdate,
    db: Session = Depends(get_db)
):
    """Update a webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Update fields
    update_data = webhook_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(webhook, field, value)
    
    webhook.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(webhook)
    
    return webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(webhook_id: int, db: Session = Depends(get_db)):
    """Delete a webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    db.delete(webhook)
    db.commit()
    
    return None


@router.get("/{webhook_id}/events", response_model=List[WebhookEventResponse])
async def get_webhook_events(
    webhook_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get events for a specific webhook"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    query = db.query(WebhookEvent).filter(WebhookEvent.webhook_id == webhook_id)
    
    if status:
        query = query.filter(WebhookEvent.status == status)
    
    events = query.order_by(WebhookEvent.received_at.desc()).offset(skip).limit(limit).all()
    return events


@router.post("/{webhook_id}/test", response_model=WebhookEventResponse)
async def test_webhook(
    webhook_id: int,
    test_request: WebhookTestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Test a webhook by sending a sample event"""
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    # Create test event
    test_event = WebhookEvent(
        webhook_id=webhook_id,
        event_type="test",
        event_data=test_request.payload,
        event_timestamp=datetime.utcnow()
    )
    
    db.add(test_event)
    webhook.total_events_received += 1
    db.commit()
    db.refresh(test_event)
    
    # Process in background
    background_tasks.add_task(webhook_service.process_webhook_event, db, test_event)
    
    return test_event


@router.post("/events/{event_id}/reprocess", response_model=WebhookEventResponse)
async def reprocess_event(
    event_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reprocess a failed webhook event"""
    event = db.query(WebhookEvent).filter(WebhookEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Reset status
    event.status = "pending"
    event.error_message = None
    db.commit()
    
    # Process in background
    background_tasks.add_task(webhook_service.process_webhook_event, db, event)
    
    return event


# Webhook receiver endpoint (for external services to POST to)
@router.post("/receive/{token}")
async def receive_webhook(
    token: str,
    request: Request,
    background_tasks: BackgroundTasks,
    x_webhook_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Receive webhook events from external services
    This is the endpoint that external services will POST to
    """
    # Find webhook by URL path
    url_path = f"/webhooks/receive/{token}"
    webhook = db.query(Webhook).filter(Webhook.url_path == url_path).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    if not webhook.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook is not active"
        )
    
    # Get request body
    body = await request.body()
    
    # Verify signature if required
    if webhook.verify_signature and webhook.secret_key:
        if not x_webhook_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature"
            )
        
        is_valid = webhook_service.verify_webhook_signature(
            body,
            x_webhook_signature,
            webhook.secret_key
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    # Parse based on provider
    if webhook.provider == "sendgrid":
        parsed_data = webhook_service.parse_sendgrid_event(payload)
    elif webhook.provider == "mailchimp":
        parsed_data = webhook_service.parse_mailchimp_event(payload)
    else:
        parsed_data = webhook_service.parse_generic_event(payload)
    
    # Create webhook event
    webhook_event = WebhookEvent(
        webhook_id=webhook.id,
        event_type=parsed_data.get("event_type", "unknown"),
        event_data=payload,
        event_timestamp=datetime.fromtimestamp(int(parsed_data.get("timestamp", 0))) if parsed_data.get("timestamp") else datetime.utcnow(),
        email=parsed_data.get("email")
    )
    
    db.add(webhook_event)
    webhook.total_events_received += 1
    webhook.last_received_at = datetime.utcnow()
    db.commit()
    db.refresh(webhook_event)
    
    # Process event in background
    background_tasks.add_task(webhook_service.process_webhook_event, db, webhook_event)
    
    return {"status": "received", "event_id": webhook_event.id}

