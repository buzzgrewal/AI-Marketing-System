"""
Lead Analytics API Routes
"""
from typing import List, Optional
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import random

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.lead_analytics import LeadAnalytics, LeadSourcePerformance
from app.schemas.lead_analytics import (
    LeadAnalyticsCreate,
    LeadAnalyticsUpdate,
    LeadAnalyticsResponse,
    LeadSourcePerformanceCreate,
    LeadSourcePerformanceResponse,
    ConversionRateData,
    ROIData,
    PerformanceMetric,
    AnalyticsSummary
)

router = APIRouter()


def calculate_metrics(analytics: LeadAnalytics) -> LeadAnalytics:
    """Calculate derived metrics for analytics"""
    if analytics.clicks > 0:
        analytics.conversion_rate = (analytics.leads_generated / analytics.clicks) * 100
    else:
        analytics.conversion_rate = 0

    if analytics.leads_generated > 0:
        analytics.cost_per_lead = analytics.cost / analytics.leads_generated
    else:
        analytics.cost_per_lead = 0

    if analytics.cost > 0:
        analytics.roi = ((analytics.revenue - analytics.cost) / analytics.cost) * 100
    else:
        analytics.roi = 0

    if analytics.impressions > 0:
        analytics.click_through_rate = (analytics.clicks / analytics.impressions) * 100
    else:
        analytics.click_through_rate = 0

    return analytics


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    period: str = Query("month", description="Period: day, week, month, year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics summary dashboard data"""
    now = datetime.utcnow()

    # Determine date range based on period
    if period == "day":
        start_date = now - timedelta(days=1)
        previous_start = start_date - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
        previous_start = start_date - timedelta(weeks=1)
    elif period == "month":
        start_date = now - timedelta(days=30)
        previous_start = start_date - timedelta(days=30)
    else:  # year
        start_date = now - timedelta(days=365)
        previous_start = start_date - timedelta(days=365)

    # Get current period data
    current_data = db.query(LeadAnalytics).filter(
        LeadAnalytics.user_id == current_user.id,
        LeadAnalytics.date >= start_date
    ).all()

    # Get previous period data for comparison
    previous_data = db.query(LeadAnalytics).filter(
        LeadAnalytics.user_id == current_user.id,
        LeadAnalytics.date >= previous_start,
        LeadAnalytics.date < start_date
    ).all()

    # Calculate aggregate metrics
    total_leads = sum(d.leads_generated for d in current_data)
    total_cost = sum(d.cost for d in current_data)
    total_revenue = sum(d.revenue for d in current_data)
    total_clicks = sum(d.clicks for d in current_data)

    prev_leads = sum(d.leads_generated for d in previous_data) or 1
    prev_cost = sum(d.cost for d in previous_data) or 1
    prev_revenue = sum(d.revenue for d in previous_data) or 1

    # Calculate average conversion rate
    avg_conversion = (total_leads / total_clicks * 100) if total_clicks > 0 else 0
    prev_conversion = sum(d.conversion_rate for d in previous_data) / len(previous_data) if previous_data else 0

    # Create performance metrics
    metrics = [
        PerformanceMetric(
            label="Total Leads",
            value=f"{total_leads:,}",
            change=((total_leads - prev_leads) / prev_leads * 100) if prev_leads > 0 else 0,
            trend="up" if total_leads > prev_leads else "down" if total_leads < prev_leads else "stable"
        ),
        PerformanceMetric(
            label="Conversion Rate",
            value=f"{avg_conversion:.1f}%",
            change=avg_conversion - prev_conversion,
            trend="up" if avg_conversion > prev_conversion else "down" if avg_conversion < prev_conversion else "stable"
        ),
        PerformanceMetric(
            label="Total Cost",
            value=f"${total_cost:,.2f}",
            change=((total_cost - prev_cost) / prev_cost * 100) if prev_cost > 0 else 0,
            trend="down" if total_cost < prev_cost else "up" if total_cost > prev_cost else "stable"
        ),
        PerformanceMetric(
            label="Revenue",
            value=f"${total_revenue:,.2f}",
            change=((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0,
            trend="up" if total_revenue > prev_revenue else "down" if total_revenue < prev_revenue else "stable"
        )
    ]

    # Get conversion rates by source
    conversion_rates = []
    roi_data = []
    source_distribution = {}

    # Group data by source
    source_groups = {}
    for record in current_data:
        if record.source not in source_groups:
            source_groups[record.source] = []
        source_groups[record.source].append(record)

    for source, records in source_groups.items():
        source_leads = sum(r.leads_generated for r in records)
        source_clicks = sum(r.clicks for r in records)
        source_cost = sum(r.cost for r in records)
        source_revenue = sum(r.revenue for r in records)

        # Conversion rate data
        if source_clicks > 0:
            conversion_rates.append(ConversionRateData(
                date=now.strftime("%Y-%m-%d"),
                rate=(source_leads / source_clicks) * 100,
                source=source
            ))

        # ROI data
        if source_cost > 0:
            roi_data.append(ROIData(
                source=source,
                roi=((source_revenue - source_cost) / source_cost) * 100,
                revenue=source_revenue,
                cost=source_cost
            ))

        # Source distribution
        source_distribution[source] = source_leads

    # Generate trend data (mock data for demonstration)
    trend_data = []
    for i in range(30):
        trend_date = (now - timedelta(days=29-i)).strftime("%Y-%m-%d")
        trend_data.append({
            "date": trend_date,
            "leads": random.randint(20, 100),
            "cost": random.uniform(100, 500),
            "revenue": random.uniform(500, 2000)
        })

    return AnalyticsSummary(
        metrics=metrics,
        conversion_rates=conversion_rates,
        roi_data=roi_data,
        source_distribution=source_distribution,
        trend_data=trend_data,
        period=period
    )


@router.get("/", response_model=List[LeadAnalyticsResponse])
async def get_analytics(
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lead analytics data"""
    query = db.query(LeadAnalytics).filter(LeadAnalytics.user_id == current_user.id)

    if source:
        query = query.filter(LeadAnalytics.source == source)

    if start_date:
        query = query.filter(LeadAnalytics.date >= start_date)

    if end_date:
        query = query.filter(LeadAnalytics.date <= end_date)

    analytics = query.order_by(desc(LeadAnalytics.date)).offset(skip).limit(limit).all()
    return analytics


@router.post("/", response_model=LeadAnalyticsResponse)
async def create_analytics(
    analytics_data: LeadAnalyticsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new analytics record"""
    db_analytics = LeadAnalytics(
        user_id=current_user.id,
        **analytics_data.dict()
    )

    # Calculate derived metrics
    db_analytics = calculate_metrics(db_analytics)

    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)

    return db_analytics


@router.put("/{analytics_id}", response_model=LeadAnalyticsResponse)
async def update_analytics(
    analytics_id: int,
    analytics_update: LeadAnalyticsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an analytics record"""
    analytics = db.query(LeadAnalytics).filter(
        LeadAnalytics.id == analytics_id,
        LeadAnalytics.user_id == current_user.id
    ).first()

    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics record not found")

    # Update fields
    update_data = analytics_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(analytics, field, value)

    # Recalculate derived metrics
    analytics = calculate_metrics(analytics)
    analytics.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(analytics)

    return analytics


@router.get("/sources", response_model=List[LeadSourcePerformanceResponse])
async def get_source_performance(
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get lead source performance data"""
    query = db.query(LeadSourcePerformance).filter(
        LeadSourcePerformance.user_id == current_user.id
    )

    if source:
        query = query.filter(LeadSourcePerformance.source == source)

    performance = query.order_by(desc(LeadSourcePerformance.period_end)).offset(skip).limit(limit).all()
    return performance


@router.post("/sources", response_model=LeadSourcePerformanceResponse)
async def create_source_performance(
    performance_data: LeadSourcePerformanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new source performance record"""
    db_performance = LeadSourcePerformance(
        user_id=current_user.id,
        **performance_data.dict()
    )

    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)

    return db_performance


@router.post("/generate-sample-data")
async def generate_sample_data(
    days: int = Query(30, description="Number of days of sample data to generate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate sample analytics data for testing"""
    sources = ["website_form", "google_ads", "facebook", "instagram", "linkedin", "email", "referral"]
    now = datetime.utcnow()

    created_records = []

    for i in range(days):
        current_date = now - timedelta(days=days-1-i)

        for source in sources:
            # Generate realistic data based on source
            base_impressions = random.randint(1000, 10000)
            ctr = random.uniform(0.01, 0.05)  # 1-5% CTR
            conversion_rate = random.uniform(0.02, 0.15)  # 2-15% conversion

            clicks = int(base_impressions * ctr)
            leads = int(clicks * conversion_rate)

            # Different cost models for different sources
            if source in ["google_ads", "facebook", "instagram"]:
                cost = random.uniform(50, 500)
            elif source == "linkedin":
                cost = random.uniform(100, 800)
            else:
                cost = random.uniform(0, 100)

            # Revenue calculation
            revenue = leads * random.uniform(50, 200)  # Average value per lead

            analytics = LeadAnalytics(
                user_id=current_user.id,
                date=current_date,
                source=source,
                impressions=base_impressions,
                clicks=clicks,
                leads_generated=leads,
                cost=cost,
                revenue=revenue
            )

            analytics = calculate_metrics(analytics)
            db.add(analytics)
            created_records.append(analytics)

    db.commit()

    return {
        "message": f"Generated {len(created_records)} sample analytics records",
        "days": days,
        "sources": sources
    }


@router.delete("/{analytics_id}")
async def delete_analytics(
    analytics_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an analytics record"""
    analytics = db.query(LeadAnalytics).filter(
        LeadAnalytics.id == analytics_id,
        LeadAnalytics.user_id == current_user.id
    ).first()

    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics record not found")

    db.delete(analytics)
    db.commit()

    return {"message": "Analytics record deleted successfully"}