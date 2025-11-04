from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.retargeting import RetargetingAudience, RetargetingEvent, RetargetingCampaign
from app.models.user import User
from app.schemas.retargeting import (
    AudienceCreate, AudienceUpdate, AudienceResponse, AudienceAnalytics,
    EventCreate, EventResponse,
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignAnalytics
)
from app.core.security import get_current_active_user
from app.services.retargeting_service import retargeting_service

router = APIRouter()


# ============= Audiences =============

@router.post("/audiences", response_model=AudienceResponse, status_code=status.HTTP_201_CREATED)
async def create_audience(
    audience_data: AudienceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new retargeting audience"""

    try:
        audience = await retargeting_service.create_audience(
            name=audience_data.name,
            description=audience_data.description,
            platform=audience_data.platform,
            criteria=audience_data.criteria,
            user_id=current_user.id,
            db=db
        )

        return audience

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audience: {str(e)}"
        )


@router.get("/audiences", response_model=List[AudienceResponse])
async def get_audiences(
    skip: int = 0,
    limit: int = 50,
    platform: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all retargeting audiences"""

    query = db.query(RetargetingAudience).filter(RetargetingAudience.user_id == current_user.id)

    if platform:
        query = query.filter(RetargetingAudience.platform == platform)

    if status_filter:
        query = query.filter(RetargetingAudience.status == status_filter)

    audiences = query.order_by(RetargetingAudience.created_at.desc()).offset(skip).limit(limit).all()
    return audiences


@router.get("/audiences/{audience_id}", response_model=AudienceResponse)
async def get_audience(
    audience_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific audience by ID"""

    audience = db.query(RetargetingAudience).filter(
        RetargetingAudience.id == audience_id,
        RetargetingAudience.user_id == current_user.id
    ).first()

    if not audience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audience not found"
        )

    return audience


@router.put("/audiences/{audience_id}", response_model=AudienceResponse)
async def update_audience(
    audience_id: int,
    audience_data: AudienceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an audience"""

    audience = db.query(RetargetingAudience).filter(
        RetargetingAudience.id == audience_id,
        RetargetingAudience.user_id == current_user.id
    ).first()

    if not audience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audience not found"
        )

    # Update fields
    update_data = audience_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(audience, field, value)

    db.commit()
    db.refresh(audience)

    return audience


@router.delete("/audiences/{audience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audience(
    audience_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an audience"""

    audience = db.query(RetargetingAudience).filter(
        RetargetingAudience.id == audience_id,
        RetargetingAudience.user_id == current_user.id
    ).first()

    if not audience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audience not found"
        )

    # Check if audience is used in active campaigns
    active_campaigns = db.query(RetargetingCampaign).filter(
        RetargetingCampaign.audience_id == audience_id,
        RetargetingCampaign.status == "active"
    ).count()

    if active_campaigns > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete audience with active campaigns"
        )

    db.delete(audience)
    db.commit()


@router.post("/audiences/{audience_id}/sync")
async def sync_audience(
    audience_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sync audience to advertising platform"""

    audience = db.query(RetargetingAudience).filter(
        RetargetingAudience.id == audience_id,
        RetargetingAudience.user_id == current_user.id
    ).first()

    if not audience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audience not found"
        )

    # Add sync task to background
    background_tasks.add_task(retargeting_service.sync_audience_to_platform, audience, db)

    return {
        "message": "Audience sync started",
        "audience_id": audience_id
    }


@router.get("/audiences/{audience_id}/analytics", response_model=AudienceAnalytics)
async def get_audience_analytics(
    audience_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for an audience"""

    audience = db.query(RetargetingAudience).filter(
        RetargetingAudience.id == audience_id,
        RetargetingAudience.user_id == current_user.id
    ).first()

    if not audience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audience not found"
        )

    try:
        analytics = retargeting_service.get_audience_analytics(audience_id, db)
        return AudienceAnalytics(**analytics)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


# ============= Events =============

@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def track_event(
    event_data: EventCreate,
    db: Session = Depends(get_db)
):
    """Track a retargeting event (public endpoint for pixel tracking)"""

    try:
        event = await retargeting_service.track_event(
            event_type=event_data.event_type,
            event_name=event_data.event_name,
            platform=event_data.platform,
            event_data=event_data.event_data or {},
            user_identifier=event_data.user_identifier,
            db=db
        )

        return event

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track event: {str(e)}"
        )


@router.get("/events", response_model=List[EventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    platform: Optional[str] = None,
    audience_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get retargeting events"""

    query = db.query(RetargetingEvent)

    if event_type:
        query = query.filter(RetargetingEvent.event_type == event_type)

    if platform:
        query = query.filter(RetargetingEvent.platform == platform)

    if audience_id:
        query = query.filter(RetargetingEvent.audience_id == audience_id)

    events = query.order_by(RetargetingEvent.event_time.desc()).offset(skip).limit(limit).all()
    return events


@router.get("/events/stats")
async def get_event_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get event statistics"""

    from datetime import timedelta
    from sqlalchemy import func

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Total events
    total_events = db.query(func.count(RetargetingEvent.id)).filter(
        RetargetingEvent.event_time >= cutoff_date
    ).scalar()

    # Events by type
    events_by_type = db.query(
        RetargetingEvent.event_type,
        func.count(RetargetingEvent.id).label('count')
    ).filter(
        RetargetingEvent.event_time >= cutoff_date
    ).group_by(
        RetargetingEvent.event_type
    ).all()

    # Total conversion value
    total_value = db.query(
        func.sum(RetargetingEvent.conversion_value)
    ).filter(
        RetargetingEvent.event_time >= cutoff_date,
        RetargetingEvent.conversion_value.isnot(None)
    ).scalar() or 0

    return {
        "days": days,
        "total_events": total_events,
        "events_by_type": {evt[0]: evt[1] for evt in events_by_type},
        "total_conversion_value": float(total_value)
    }


# ============= Campaigns =============

@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new retargeting campaign"""

    # Verify audience exists and belongs to user
    audience = db.query(RetargetingAudience).filter(
        RetargetingAudience.id == campaign_data.audience_id,
        RetargetingAudience.user_id == current_user.id
    ).first()

    if not audience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audience not found"
        )

    try:
        campaign = await retargeting_service.create_campaign(
            name=campaign_data.name,
            audience_id=campaign_data.audience_id,
            platform=campaign_data.platform,
            ad_creative=campaign_data.ad_creative or {},
            budget_daily=campaign_data.budget_daily,
            user_id=current_user.id,
            db=db
        )

        # Set additional fields
        if campaign_data.description:
            campaign.description = campaign_data.description
        if campaign_data.budget_total:
            campaign.budget_total = campaign_data.budget_total
        if campaign_data.start_date:
            campaign.start_date = campaign_data.start_date
        if campaign_data.end_date:
            campaign.end_date = campaign_data.end_date

        campaign.currency = campaign_data.currency

        db.commit()
        db.refresh(campaign)

        return campaign

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


@router.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    skip: int = 0,
    limit: int = 50,
    platform: Optional[str] = None,
    status_filter: Optional[str] = None,
    audience_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all retargeting campaigns"""

    query = db.query(RetargetingCampaign).filter(RetargetingCampaign.user_id == current_user.id)

    if platform:
        query = query.filter(RetargetingCampaign.platform == platform)

    if status_filter:
        query = query.filter(RetargetingCampaign.status == status_filter)

    if audience_id:
        query = query.filter(RetargetingCampaign.audience_id == audience_id)

    campaigns = query.order_by(RetargetingCampaign.created_at.desc()).offset(skip).limit(limit).all()
    return campaigns


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific campaign by ID"""

    campaign = db.query(RetargetingCampaign).filter(
        RetargetingCampaign.id == campaign_id,
        RetargetingCampaign.user_id == current_user.id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    return campaign


@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a campaign"""

    campaign = db.query(RetargetingCampaign).filter(
        RetargetingCampaign.id == campaign_id,
        RetargetingCampaign.user_id == current_user.id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Update fields
    update_data = campaign_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)

    db.commit()
    db.refresh(campaign)

    return campaign


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a campaign"""

    campaign = db.query(RetargetingCampaign).filter(
        RetargetingCampaign.id == campaign_id,
        RetargetingCampaign.user_id == current_user.id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    if campaign.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active campaign. Pause it first."
        )

    db.delete(campaign)
    db.commit()


@router.get("/campaigns/{campaign_id}/analytics", response_model=CampaignAnalytics)
async def get_campaign_analytics(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a campaign"""

    campaign = db.query(RetargetingCampaign).filter(
        RetargetingCampaign.id == campaign_id,
        RetargetingCampaign.user_id == current_user.id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    try:
        analytics = retargeting_service.get_campaign_analytics(campaign_id, db)
        return CampaignAnalytics(**analytics)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Pause a campaign"""

    campaign = db.query(RetargetingCampaign).filter(
        RetargetingCampaign.id == campaign_id,
        RetargetingCampaign.user_id == current_user.id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    campaign.status = "paused"
    db.commit()

    return {"message": "Campaign paused", "campaign_id": campaign_id}


@router.post("/campaigns/{campaign_id}/activate")
async def activate_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Activate a campaign"""

    campaign = db.query(RetargetingCampaign).filter(
        RetargetingCampaign.id == campaign_id,
        RetargetingCampaign.user_id == current_user.id
    ).first()

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    campaign.status = "active"
    if not campaign.start_date:
        campaign.start_date = datetime.utcnow()

    db.commit()

    return {"message": "Campaign activated", "campaign_id": campaign_id}
