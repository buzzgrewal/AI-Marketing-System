from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.campaign import Campaign, EmailLog
from app.models.lead import Lead
from app.models.user import User
from app.models.email_template import EmailTemplate
from app.models.segment import Segment
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignStats
from app.core.security import get_current_active_user
from app.services.email_service import email_service
from app.services.template_service import template_service
from app.services.segment_service import segment_service

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: Session = Depends(get_db)
):
    """Create a new campaign"""

    new_campaign = Campaign(
        **campaign_data.dict(),
        created_by=None
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    return new_campaign


@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 50,
    campaign_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all campaigns with filters"""

    query = db.query(Campaign)

    if campaign_type:
        query = query.filter(Campaign.campaign_type == campaign_type)

    if status:
        query = query.filter(Campaign.status == status)

    campaigns = query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get specific campaign by ID"""

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    db: Session = Depends(get_db)
):
    """Update a campaign"""

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Don't allow updating sent campaigns
    if campaign.status in ["completed", "active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update active or completed campaigns"
        )

    # Update fields
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)

    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Delete a campaign"""

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Don't allow deleting active campaigns
    if campaign.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active campaigns"
        )

    db.delete(campaign)
    db.commit()

    return None


@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send campaign to opted-in leads"""

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    if campaign.campaign_type != "email":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only email campaigns can be sent through this endpoint"
        )

    if campaign.status not in ["draft", "scheduled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign has already been sent or is not ready"
        )

    # Get targeted leads based on segment or filters
    if campaign.segment_id:
        # Use segment to get leads
        segment = db.query(Segment).filter(Segment.id == campaign.segment_id).first()
        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found"
            )
        
        # Get all leads matching segment
        all_segment_leads = segment_service.get_segment_leads(campaign.segment_id, db)
        
        # Filter for email consent
        leads = [lead for lead in all_segment_leads if lead.email_consent]
        
        # Update segment usage
        segment.campaign_count += 1
        segment.last_used = datetime.utcnow()
        db.commit()
    else:
        # Use traditional filters (only those with email consent)
        query = db.query(Lead).filter(Lead.email_consent == True)

        # Apply targeting filters
        if campaign.target_sport_type:
            query = query.filter(Lead.sport_type == campaign.target_sport_type)

        leads = query.all()

    if not leads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No opted-in leads match the campaign criteria"
        )

    # If campaign uses a template, render it with lead data
    # Otherwise use the campaign content directly
    if campaign.template_id:
        template = db.query(EmailTemplate).filter(EmailTemplate.id == campaign.template_id).first()
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        # Mark template as used
        template.usage_count += 1
        template.last_used_at = datetime.utcnow()
    
    # Update campaign status and counts
    campaign.status = "active"
    campaign.total_recipients = len(leads)
    campaign.sent_date = datetime.utcnow()
    db.commit()

    # Prepare recipients list with lead data for template rendering
    recipients = [
        {
            "email": lead.email,
            "lead_id": lead.id,
            "lead_data": {
                "first_name": lead.first_name or "",
                "last_name": lead.last_name or "",
                "email": lead.email,
                "sport_type": lead.sport_type or "",
                "customer_type": lead.customer_type or "",
                "location": lead.location or "",
            }
        }
        for lead in leads
    ]

    # Send emails in background
    background_tasks.add_task(
        send_campaign_emails,
        campaign_id=campaign.id,
        subject=campaign.subject,
        content=campaign.content,
        template_id=campaign.template_id,
        recipients=recipients,
        db=db
    )

    return {
        "message": "Campaign is being sent",
        "total_recipients": len(recipients)
    }


async def send_campaign_emails(
    campaign_id: int,
    subject: str,
    content: str,
    template_id: Optional[int],
    recipients: list,
    db: Session
):
    """Background task to send campaign emails"""

    # Get template if template_id is provided
    template = None
    if template_id:
        template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()

    # Send emails to each recipient
    sent_count = 0
    failed_count = 0
    
    for recipient in recipients:
        try:
            # Determine subject and content
            email_subject = subject
            email_content = content
            
            # If using a template, render it with recipient's data
            if template:
                lead_data = recipient.get("lead_data", {})
                variables = template_service.prepare_variables(lead_data)
                email_subject = template_service.render_template(template.subject, variables)
                email_content = template_service.render_template(template.html_content, variables)
            else:
                # Wrap custom content in email template
                email_content = email_service.create_email_template(content)
            
            # Send individual email
            success = await email_service.send_email(
                to_email=recipient["email"],
                subject=email_subject,
                body=email_content,
                campaign_id=campaign_id,
                lead_id=recipient.get("lead_id"),
                db=db
            )
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            print(f"Error sending email to {recipient['email']}: {str(e)}")
            failed_count += 1

    # Update campaign statistics
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if campaign:
        campaign.total_sent = sent_count
        campaign.total_delivered = sent_count  # Will be updated by webhook/tracking
        if sent_count == campaign.total_recipients:
            campaign.status = "completed"
        db.commit()


@router.get("/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed campaign statistics"""

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Get email logs
    email_logs = db.query(EmailLog).filter(EmailLog.campaign_id == campaign_id).all()

    # Calculate rates
    open_rate = (campaign.total_opened / campaign.total_delivered * 100) if campaign.total_delivered > 0 else 0
    click_rate = (campaign.total_clicked / campaign.total_delivered * 100) if campaign.total_delivered > 0 else 0
    conversion_rate = (campaign.total_converted / campaign.total_delivered * 100) if campaign.total_delivered > 0 else 0

    return {
        "campaign": campaign,
        "metrics": {
            "total_recipients": campaign.total_recipients,
            "total_sent": campaign.total_sent,
            "total_delivered": campaign.total_delivered,
            "total_opened": campaign.total_opened,
            "total_clicked": campaign.total_clicked,
            "total_converted": campaign.total_converted,
            "total_unsubscribed": campaign.total_unsubscribed,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "conversion_rate": round(conversion_rate, 2)
        },
        "timeline": {
            "created_at": campaign.created_at,
            "scheduled_date": campaign.scheduled_date,
            "sent_date": campaign.sent_date
        }
    }


@router.get("/stats/overview")
async def get_campaigns_overview(
    db: Session = Depends(get_db)
):
    """Get overview statistics for all campaigns"""

    campaigns = db.query(Campaign).all()

    total_campaigns = len(campaigns)
    active_campaigns = len([c for c in campaigns if c.status == "active"])

    total_sent = sum(c.total_sent for c in campaigns)
    total_delivered = sum(c.total_delivered for c in campaigns)
    total_opened = sum(c.total_opened for c in campaigns)
    total_clicked = sum(c.total_clicked for c in campaigns)
    total_converted = sum(c.total_converted for c in campaigns)

    avg_open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
    avg_click_rate = (total_clicked / total_delivered * 100) if total_delivered > 0 else 0
    avg_conversion_rate = (total_converted / total_delivered * 100) if total_delivered > 0 else 0

    return {
        "total_campaigns": total_campaigns,
        "active_campaigns": active_campaigns,
        "total_sent": total_sent,
        "avg_open_rate": round(avg_open_rate, 2),
        "avg_click_rate": round(avg_click_rate, 2),
        "avg_conversion_rate": round(avg_conversion_rate, 2)
    }
