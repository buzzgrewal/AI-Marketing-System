from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.lead import Lead
from app.models.lead_tracking import (
    LeadLifecycle, LeadScore, EngagementHistory,
    LeadAttribution, LeadJourney, LeadActivitySummary
)
from app.services.lead_tracking_service import lead_tracking_service

router = APIRouter()


# ============= Lifecycle Management =============

@router.post("/lifecycle/{lead_id}/transition")
async def transition_lead_stage(
    lead_id: int,
    new_stage: str,
    reason: Optional[str] = None,
    triggered_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Transition a lead to a new lifecycle stage"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        lifecycle = lead_tracking_service.transition_lead_stage(
            lead=lead,
            new_stage=new_stage,
            reason=reason,
            triggered_by=triggered_by,
            db=db
        )

        return {
            "message": "Lead stage transitioned successfully",
            "lead_id": lead_id,
            "new_stage": new_stage,
            "previous_stage": lifecycle.previous_stage,
            "lifecycle": {
                "id": lifecycle.id,
                "stage": lifecycle.stage,
                "entered_at": lifecycle.entered_at.isoformat() if lifecycle.entered_at else None,
                "transition_reason": lifecycle.transition_reason
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transition stage: {str(e)}"
        )


@router.get("/lifecycle/{lead_id}/history")
async def get_lifecycle_history(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get complete lifecycle history for a lead"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    history = lead_tracking_service.get_lead_lifecycle_history(lead_id, db)

    return {
        "lead_id": lead_id,
        "total_stages": len(history),
        "history": [
            {
                "id": lc.id,
                "stage": lc.stage,
                "previous_stage": lc.previous_stage,
                "entered_at": lc.entered_at.isoformat() if lc.entered_at else None,
                "exited_at": lc.exited_at.isoformat() if lc.exited_at else None,
                "duration_days": lc.duration_days,
                "touchpoints_count": lc.touchpoints_count,
                "engagement_score": lc.engagement_score,
                "transition_reason": lc.transition_reason,
                "is_current_stage": lc.is_current_stage
            }
            for lc in history
        ]
    }


@router.get("/lifecycle/{lead_id}/current")
async def get_current_stage(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get current lifecycle stage for a lead"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    current_stage = lead_tracking_service.get_current_stage(lead_id, db)

    if not current_stage:
        return {
            "lead_id": lead_id,
            "current_stage": None,
            "message": "No lifecycle tracking found for this lead"
        }

    return {
        "lead_id": lead_id,
        "current_stage": {
            "stage": current_stage.stage,
            "entered_at": current_stage.entered_at.isoformat() if current_stage.entered_at else None,
            "days_in_stage": (datetime.utcnow() - current_stage.entered_at).days if current_stage.entered_at else 0,
            "touchpoints_count": current_stage.touchpoints_count,
            "engagement_score": current_stage.engagement_score
        }
    }


# ============= Lead Scoring =============

@router.post("/scoring/{lead_id}/calculate")
async def calculate_lead_score(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Calculate comprehensive lead score"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        lead_score = lead_tracking_service.calculate_lead_score(lead, db)

        return {
            "lead_id": lead_id,
            "score": {
                "total_score": lead_score.total_score,
                "grade": lead_score.grade,
                "temperature": lead_score.temperature,
                "components": {
                    "demographic": lead_score.demographic_score,
                    "behavioral": lead_score.behavioral_score,
                    "firmographic": lead_score.firmographic_score,
                    "engagement": lead_score.engagement_score,
                    "intent": lead_score.intent_score
                },
                "previous_score": lead_score.previous_score,
                "score_changed": lead_score.score_changed,
                "score_change_amount": lead_score.score_change_amount,
                "last_calculated_at": lead_score.last_calculated_at.isoformat() if lead_score.last_calculated_at else None,
                "score_factors": lead_score.score_factors
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate score: {str(e)}"
        )


@router.get("/scoring/{lead_id}")
async def get_lead_score(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get current lead score"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    lead_score = db.query(LeadScore).filter(
        LeadScore.lead_id == lead_id
    ).first()

    if not lead_score:
        return {
            "lead_id": lead_id,
            "score": None,
            "message": "No score calculated yet. Call POST /scoring/{lead_id}/calculate first."
        }

    return {
        "lead_id": lead_id,
        "score": {
            "total_score": lead_score.total_score,
            "grade": lead_score.grade,
            "temperature": lead_score.temperature,
            "components": {
                "demographic": lead_score.demographic_score,
                "behavioral": lead_score.behavioral_score,
                "firmographic": lead_score.firmographic_score,
                "engagement": lead_score.engagement_score,
                "intent": lead_score.intent_score
            },
            "last_calculated_at": lead_score.last_calculated_at.isoformat() if lead_score.last_calculated_at else None
        }
    }


@router.post("/scoring/bulk-calculate")
async def bulk_calculate_scores(
    lead_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db)
):
    """Calculate scores for multiple leads"""

    if lead_ids:
        leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
    else:
        leads = db.query(Lead).all()

    results = {
        "total_leads": len(leads),
        "calculated": 0,
        "failed": 0,
        "scores": []
    }

    for lead in leads:
        try:
            lead_score = lead_tracking_service.calculate_lead_score(lead, db)
            results["calculated"] += 1
            results["scores"].append({
                "lead_id": lead.id,
                "total_score": lead_score.total_score,
                "grade": lead_score.grade,
                "temperature": lead_score.temperature
            })
        except Exception as e:
            results["failed"] += 1
            print(f"Error calculating score for lead {lead.id}: {str(e)}")

    return results


# ============= Engagement Tracking =============

@router.post("/engagement/{lead_id}")
async def track_engagement(
    lead_id: int,
    engagement_type: str,
    engagement_channel: Optional[str] = None,
    source_type: Optional[str] = None,
    source_id: Optional[int] = None,
    source_name: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    event_metadata: Optional[dict] = None,
    engagement_value: int = 0,
    revenue_attributed: float = 0.0,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    device_type: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Track a lead engagement event"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        engagement = lead_tracking_service.track_engagement(
            lead_id=lead_id,
            engagement_type=engagement_type,
            engagement_channel=engagement_channel,
            source_type=source_type,
            source_id=source_id,
            source_name=source_name,
            title=title,
            description=description,
            event_metadata=event_metadata,
            engagement_value=engagement_value,
            revenue_attributed=revenue_attributed,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            location=location,
            db=db
        )

        return {
            "message": "Engagement tracked successfully",
            "engagement_id": engagement.id,
            "lead_id": lead_id,
            "engagement_type": engagement_type,
            "engaged_at": engagement.engaged_at.isoformat() if engagement.engaged_at else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track engagement: {str(e)}"
        )


@router.get("/engagement/{lead_id}/history")
async def get_engagement_history(
    lead_id: int,
    days: int = 90,
    engagement_types: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """Get engagement history for a lead"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    history = lead_tracking_service.get_engagement_history(
        lead_id=lead_id,
        days=days,
        engagement_types=engagement_types,
        db=db
    )

    return {
        "lead_id": lead_id,
        "total_engagements": len(history),
        "period_days": days,
        "engagements": [
            {
                "id": e.id,
                "engagement_type": e.engagement_type,
                "engagement_channel": e.engagement_channel,
                "source_type": e.source_type,
                "source_name": e.source_name,
                "title": e.title,
                "description": e.description,
                "engagement_value": e.engagement_value,
                "revenue_attributed": e.revenue_attributed,
                "engaged_at": e.engaged_at.isoformat() if e.engaged_at else None,
                "device_type": e.device_type,
                "location": e.location
            }
            for e in history
        ]
    }


@router.get("/engagement/stats/summary")
async def get_engagement_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get engagement statistics summary"""

    from sqlalchemy import func

    # Get engagement counts by type
    engagement_counts = db.query(
        EngagementHistory.engagement_type,
        func.count(EngagementHistory.id).label('count')
    ).filter(
        EngagementHistory.engaged_at >= datetime.utcnow() - timedelta(days=days)
    ).group_by(
        EngagementHistory.engagement_type
    ).all()

    # Get engagement counts by channel
    channel_counts = db.query(
        EngagementHistory.engagement_channel,
        func.count(EngagementHistory.id).label('count')
    ).filter(
        EngagementHistory.engaged_at >= datetime.utcnow() - timedelta(days=days)
    ).group_by(
        EngagementHistory.engagement_channel
    ).all()

    # Total engagements
    total_engagements = db.query(EngagementHistory).filter(
        EngagementHistory.engaged_at >= datetime.utcnow() - timedelta(days=days)
    ).count()

    # Total revenue attributed
    total_revenue = db.query(
        func.sum(EngagementHistory.revenue_attributed)
    ).filter(
        EngagementHistory.engaged_at >= datetime.utcnow() - timedelta(days=days)
    ).scalar() or 0.0

    return {
        "period_days": days,
        "total_engagements": total_engagements,
        "total_revenue_attributed": float(total_revenue),
        "by_type": {
            e_type: count for e_type, count in engagement_counts
        },
        "by_channel": {
            channel: count for channel, count in channel_counts if channel
        }
    }


# ============= Attribution Tracking =============

from pydantic import BaseModel

class AttributionRequest(BaseModel):
    conversion_type: str
    conversion_value: float
    attribution_model: str = "linear"

@router.post("/attribution/{lead_id}/calculate")
async def calculate_attribution(
    lead_id: int,
    request: AttributionRequest,
    db: Session = Depends(get_db)
):
    """Calculate multi-touch attribution for a conversion"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        attribution = lead_tracking_service.calculate_attribution(
            lead_id=lead_id,
            conversion_type=request.conversion_type,
            conversion_value=request.conversion_value,
            attribution_model=request.attribution_model,
            db=db
        )

        if not attribution:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No touchpoints found for this lead"
            )

        return {
            "message": "Attribution calculated successfully",
            "lead_id": lead_id,
            "attribution": {
                "id": attribution.id,
                "conversion_type": attribution.conversion_type,
                "conversion_value": attribution.conversion_value,
                "attribution_model": attribution.attribution_model,
                "total_touchpoints": attribution.total_touchpoints,
                "journey_duration_days": attribution.journey_duration_days,
                "first_touch": {
                    "source": attribution.first_touch_source,
                    "name": attribution.first_touch_name,
                    "date": attribution.first_touch_date.isoformat() if attribution.first_touch_date else None,
                    "weight": attribution.first_touch_weight
                },
                "last_touch": {
                    "source": attribution.last_touch_source,
                    "name": attribution.last_touch_name,
                    "date": attribution.last_touch_date.isoformat() if attribution.last_touch_date else None,
                    "weight": attribution.last_touch_weight
                },
                "primary_touchpoint": attribution.primary_touchpoint,
                "secondary_touchpoint": attribution.secondary_touchpoint,
                "touchpoints": attribution.touchpoints
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate attribution: {str(e)}"
        )


@router.get("/attribution/{lead_id}")
async def get_attribution_history(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get attribution history for a lead"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    attributions = db.query(LeadAttribution).filter(
        LeadAttribution.lead_id == lead_id
    ).order_by(LeadAttribution.conversion_date.desc()).all()

    return {
        "lead_id": lead_id,
        "total_conversions": len(attributions),
        "attributions": [
            {
                "id": attr.id,
                "conversion_type": attr.conversion_type,
                "conversion_value": attr.conversion_value,
                "conversion_date": attr.conversion_date.isoformat() if attr.conversion_date else None,
                "attribution_model": attr.attribution_model,
                "total_touchpoints": attr.total_touchpoints,
                "journey_duration_days": attr.journey_duration_days,
                "primary_touchpoint": attr.primary_touchpoint
            }
            for attr in attributions
        ]
    }


@router.get("/attribution/stats/summary")
async def get_attribution_summary(
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get attribution statistics summary"""

    from sqlalchemy import func

    # Get conversions by type
    conversions_by_type = db.query(
        LeadAttribution.conversion_type,
        func.count(LeadAttribution.id).label('count'),
        func.sum(LeadAttribution.conversion_value).label('total_value')
    ).filter(
        LeadAttribution.conversion_date >= datetime.utcnow() - timedelta(days=days)
    ).group_by(
        LeadAttribution.conversion_type
    ).all()

    # Total conversions and revenue
    total_conversions = db.query(LeadAttribution).filter(
        LeadAttribution.conversion_date >= datetime.utcnow() - timedelta(days=days)
    ).count()

    total_revenue = db.query(
        func.sum(LeadAttribution.conversion_value)
    ).filter(
        LeadAttribution.conversion_date >= datetime.utcnow() - timedelta(days=days)
    ).scalar() or 0.0

    # Average journey duration
    avg_journey = db.query(
        func.avg(LeadAttribution.journey_duration_days)
    ).filter(
        LeadAttribution.conversion_date >= datetime.utcnow() - timedelta(days=days)
    ).scalar() or 0.0

    return {
        "period_days": days,
        "total_conversions": total_conversions,
        "total_revenue": float(total_revenue),
        "average_journey_days": float(avg_journey),
        "conversions_by_type": [
            {
                "type": c_type,
                "count": count,
                "total_value": float(total_value or 0)
            }
            for c_type, count, total_value in conversions_by_type
        ]
    }


# ============= Journey Tracking =============

@router.get("/journey/{lead_id}")
async def get_lead_journey(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get complete lead journey"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    journey = lead_tracking_service.get_lead_journey(lead_id, db)

    if not journey:
        return {
            "lead_id": lead_id,
            "journey": None,
            "message": "No journey tracking found for this lead"
        }

    return {
        "lead_id": lead_id,
        "journey": {
            "journey_start_date": journey.journey_start_date.isoformat() if journey.journey_start_date else None,
            "last_activity_date": journey.last_activity_date.isoformat() if journey.last_activity_date else None,
            "journey_duration_days": journey.journey_duration_days,
            "current_stage": journey.current_stage,
            "stages_completed": journey.stages_completed,
            "milestones": journey.milestones,
            "metrics": {
                "total_engagements": journey.total_engagements,
                "total_touchpoints": journey.total_touchpoints,
                "email_engagements": journey.email_engagements,
                "form_submissions": journey.form_submissions,
                "page_views": journey.page_views,
                "purchases": journey.purchases
            },
            "health": {
                "engagement_trend": journey.engagement_trend,
                "days_since_last_activity": journey.days_since_last_activity,
                "risk_of_churn": journey.risk_of_churn
            },
            "revenue": {
                "lifetime_value": journey.lifetime_value,
                "total_revenue": journey.total_revenue,
                "predicted_value": journey.predicted_value
            }
        }
    }


@router.get("/journey/stats/overview")
async def get_journey_stats(
    db: Session = Depends(get_db)
):
    """Get journey statistics overview"""

    from sqlalchemy import func

    # Total journeys
    total_journeys = db.query(LeadJourney).count()

    # Average journey duration
    avg_duration = db.query(
        func.avg(LeadJourney.journey_duration_days)
    ).scalar() or 0.0

    # Engagement trends
    trend_counts = db.query(
        LeadJourney.engagement_trend,
        func.count(LeadJourney.id).label('count')
    ).group_by(
        LeadJourney.engagement_trend
    ).all()

    # High churn risk leads
    high_risk = db.query(LeadJourney).filter(
        LeadJourney.risk_of_churn >= 0.7
    ).count()

    # Total lifetime value
    total_ltv = db.query(
        func.sum(LeadJourney.lifetime_value)
    ).scalar() or 0.0

    return {
        "total_journeys": total_journeys,
        "average_journey_days": float(avg_duration),
        "engagement_trends": {
            trend: count for trend, count in trend_counts
        },
        "high_risk_count": high_risk,
        "total_lifetime_value": float(total_ltv)
    }


# ============= Analytics & Reports =============

@router.get("/analytics/funnel")
async def get_lifecycle_funnel(
    days: int = 90,
    db: Session = Depends(get_db)
):
    """Get lifecycle stage funnel metrics"""

    from sqlalchemy import func

    # Get counts by current stage
    stage_counts = db.query(
        LeadLifecycle.stage,
        func.count(LeadLifecycle.id).label('count')
    ).filter(
        LeadLifecycle.is_current_stage == True
    ).group_by(
        LeadLifecycle.stage
    ).all()

    # Get average duration by stage
    stage_durations = db.query(
        LeadLifecycle.stage,
        func.avg(LeadLifecycle.duration_days).label('avg_duration')
    ).filter(
        LeadLifecycle.duration_days.isnot(None)
    ).group_by(
        LeadLifecycle.stage
    ).all()

    return {
        "funnel": [
            {
                "stage": stage,
                "count": count
            }
            for stage, count in stage_counts
        ],
        "average_durations": {
            stage: float(avg_duration or 0)
            for stage, avg_duration in stage_durations
        }
    }


@router.get("/analytics/cohort")
async def get_cohort_analysis(
    cohort_type: str = "monthly",
    db: Session = Depends(get_db)
):
    """Get cohort analysis data"""

    from sqlalchemy import func, extract

    # Group leads by creation month
    if cohort_type == "monthly":
        cohorts = db.query(
            func.date_trunc('month', Lead.created_at).label('cohort'),
            func.count(Lead.id).label('total_leads'),
            func.sum(func.cast(Lead.status == 'customer', db.Integer)).label('customers')
        ).group_by(
            func.date_trunc('month', Lead.created_at)
        ).order_by(
            func.date_trunc('month', Lead.created_at).desc()
        ).limit(12).all()

        return {
            "cohort_type": cohort_type,
            "cohorts": [
                {
                    "cohort": cohort.isoformat() if cohort else None,
                    "total_leads": total_leads,
                    "customers": customers or 0,
                    "conversion_rate": round((customers or 0) / total_leads * 100, 2) if total_leads > 0 else 0
                }
                for cohort, total_leads, customers in cohorts
            ]
        }

    return {"error": "Invalid cohort_type. Use 'monthly' or 'weekly'"}


@router.get("/analytics/lead-quality")
async def get_lead_quality_distribution(
    db: Session = Depends(get_db)
):
    """Get lead quality score distribution"""

    from sqlalchemy import func

    # Get distribution by grade
    grade_distribution = db.query(
        LeadScore.grade,
        func.count(LeadScore.id).label('count')
    ).group_by(
        LeadScore.grade
    ).all()

    # Get distribution by temperature
    temp_distribution = db.query(
        LeadScore.temperature,
        func.count(LeadScore.id).label('count')
    ).group_by(
        LeadScore.temperature
    ).all()

    # Average score
    avg_score = db.query(
        func.avg(LeadScore.total_score)
    ).scalar() or 0.0

    return {
        "average_score": float(avg_score),
        "by_grade": {
            grade: count for grade, count in grade_distribution
        },
        "by_temperature": {
            temp: count for temp, count in temp_distribution if temp
        }
    }
