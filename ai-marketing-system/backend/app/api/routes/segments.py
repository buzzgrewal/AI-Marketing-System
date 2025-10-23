from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.segment import Segment
from app.models.lead import Lead
from app.schemas.segment import (
    SegmentCreate,
    SegmentUpdate,
    SegmentResponse,
    SegmentPreviewRequest,
    SegmentPreviewResponse,
    SegmentFieldsResponse,
    SegmentStatsResponse,
    SegmentField
)
from app.services.segment_service import segment_service

router = APIRouter()


@router.post("/", response_model=SegmentResponse, status_code=status.HTTP_201_CREATED)
async def create_segment(
    segment_data: SegmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new segment"""
    
    # Validate criteria
    validation = segment_service.validate_criteria(segment_data.criteria.model_dump())
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid criteria: {', '.join(validation['errors'])}"
        )
    
    # Create segment
    new_segment = Segment(
        name=segment_data.name,
        description=segment_data.description,
        criteria=segment_data.criteria.model_dump(),
        segment_type=segment_data.segment_type,
        is_active=segment_data.is_active,
        tags=segment_data.tags,
        created_by=None
    )
    
    db.add(new_segment)
    db.commit()
    db.refresh(new_segment)
    
    # Calculate initial lead count
    segment_service.update_segment_count(new_segment.id, db)
    db.refresh(new_segment)
    
    return new_segment


@router.get("/", response_model=List[SegmentResponse])
async def get_segments(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all segments with optional filters"""
    
    query = db.query(Segment)
    
    if is_active is not None:
        query = query.filter(Segment.is_active == is_active)
    
    if search:
        query = query.filter(
            (Segment.name.ilike(f"%{search}%")) |
            (Segment.description.ilike(f"%{search}%"))
        )
    
    segments = query.order_by(Segment.created_at.desc()).offset(skip).limit(limit).all()
    return segments


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(
    segment_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific segment"""
    
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )
    
    return segment


@router.put("/{segment_id}", response_model=SegmentResponse)
async def update_segment(
    segment_id: int,
    segment_data: SegmentUpdate,
    db: Session = Depends(get_db)
):
    """Update a segment"""
    
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )
    
    # Update fields
    update_dict = segment_data.model_dump(exclude_unset=True)
    
    # Validate criteria if being updated
    if "criteria" in update_dict:
        validation = segment_service.validate_criteria(update_dict["criteria"].model_dump())
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid criteria: {', '.join(validation['errors'])}"
            )
        update_dict["criteria"] = update_dict["criteria"].model_dump()
    
    for field, value in update_dict.items():
        setattr(segment, field, value)
    
    segment.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Recalculate lead count if criteria changed
    if "criteria" in update_dict:
        segment_service.update_segment_count(segment.id, db)
    
    db.refresh(segment)
    
    return segment


@router.delete("/{segment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_segment(
    segment_id: int,
    db: Session = Depends(get_db)
):
    """Delete a segment"""
    
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )
    
    db.delete(segment)
    db.commit()
    
    return None


@router.post("/preview", response_model=SegmentPreviewResponse)
async def preview_segment(
    request: SegmentPreviewRequest,
    db: Session = Depends(get_db)
):
    """Preview leads matching segment criteria"""
    
    # Validate criteria
    validation = segment_service.validate_criteria(request.criteria.model_dump())
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid criteria: {', '.join(validation['errors'])}"
        )
    
    # Get matching leads
    matching_leads = segment_service.get_matching_leads(
        request.criteria.model_dump(),
        db,
        limit=request.limit
    )
    
    # Count total matches
    total_matches = segment_service.count_matching_leads(request.criteria.model_dump(), db)
    
    # Format leads for response
    leads_data = [
        {
            "id": lead.id,
            "email": lead.email,
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "sport_type": lead.sport_type,
            "customer_type": lead.customer_type,
            "status": lead.status,
            "location": lead.location,
        }
        for lead in matching_leads
    ]
    
    return SegmentPreviewResponse(
        total_matches=total_matches,
        leads=leads_data
    )


@router.post("/{segment_id}/refresh")
async def refresh_segment_count(
    segment_id: int,
    db: Session = Depends(get_db)
):
    """Recalculate lead count for a segment"""
    
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )
    
    segment_service.update_segment_count(segment_id, db)
    db.refresh(segment)
    
    return {
        "message": "Segment count refreshed",
        "lead_count": segment.lead_count,
        "last_calculated": segment.last_calculated
    }


@router.get("/{segment_id}/leads")
async def get_segment_leads(
    segment_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all leads in a segment"""
    
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )
    
    leads = segment_service.get_segment_leads(segment_id, db, limit)
    
    return {
        "segment_id": segment_id,
        "segment_name": segment.name,
        "total_leads": len(leads),
        "leads": [
            {
                "id": lead.id,
                "email": lead.email,
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "sport_type": lead.sport_type,
                "customer_type": lead.customer_type,
                "status": lead.status,
            }
            for lead in leads
        ]
    }


@router.get("/fields/available", response_model=SegmentFieldsResponse)
async def get_available_fields():
    """Get list of available fields for segmentation"""
    
    fields = segment_service.get_available_fields()
    
    return SegmentFieldsResponse(
        fields=[SegmentField(**field) for field in fields]
    )


@router.get("/stats/overview", response_model=SegmentStatsResponse)
async def get_segment_stats(
    db: Session = Depends(get_db)
):
    """Get segment statistics"""
    
    total_segments = db.query(Segment).count()
    active_segments = db.query(Segment).filter(Segment.is_active == True).count()
    
    # Get total unique leads covered
    segments = db.query(Segment).all()
    all_lead_ids = set()
    for segment in segments:
        leads = segment_service.get_segment_leads(segment.id, db)
        all_lead_ids.update(lead.id for lead in leads)
    
    # Get most used segment
    most_used = db.query(Segment).order_by(Segment.campaign_count.desc()).first()
    most_used_data = None
    if most_used:
        most_used_data = {
            "id": most_used.id,
            "name": most_used.name,
            "campaign_count": most_used.campaign_count
        }
    
    return SegmentStatsResponse(
        total_segments=total_segments,
        active_segments=active_segments,
        total_leads_covered=len(all_lead_ids),
        most_used_segment=most_used_data
    )


@router.post("/{segment_id}/duplicate", response_model=SegmentResponse)
async def duplicate_segment(
    segment_id: int,
    db: Session = Depends(get_db)
):
    """Duplicate a segment"""
    
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Segment not found"
        )
    
    # Create duplicate
    new_segment = Segment(
        name=f"{segment.name} (Copy)",
        description=segment.description,
        criteria=segment.criteria,
        segment_type=segment.segment_type,
        is_active=True,
        tags=segment.tags,
        created_by=None
    )
    
    db.add(new_segment)
    db.commit()
    db.refresh(new_segment)
    
    # Calculate lead count
    segment_service.update_segment_count(new_segment.id, db)
    db.refresh(new_segment)
    
    return new_segment

