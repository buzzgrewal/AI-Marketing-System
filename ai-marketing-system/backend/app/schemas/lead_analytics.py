"""
Lead Analytics Schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class LeadAnalyticsBase(BaseModel):
    """Base schema for lead analytics"""
    date: datetime
    source: str
    impressions: int = 0
    clicks: int = 0
    leads_generated: int = 0
    cost: float = 0.0
    revenue: float = 0.0


class LeadAnalyticsCreate(LeadAnalyticsBase):
    """Schema for creating lead analytics record"""
    pass


class LeadAnalyticsUpdate(BaseModel):
    """Schema for updating lead analytics"""
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    leads_generated: Optional[int] = None
    cost: Optional[float] = None
    revenue: Optional[float] = None


class LeadAnalyticsResponse(LeadAnalyticsBase):
    """Schema for lead analytics response"""
    id: int
    user_id: int
    conversion_rate: float
    cost_per_lead: float
    roi: float
    click_through_rate: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadSourcePerformanceBase(BaseModel):
    """Base schema for lead source performance"""
    source: str
    source_id: Optional[str] = None
    period_start: datetime
    period_end: datetime
    total_leads: int = 0
    qualified_leads: int = 0
    converted_leads: int = 0
    total_cost: float = 0.0
    total_revenue: float = 0.0


class LeadSourcePerformanceCreate(LeadSourcePerformanceBase):
    """Schema for creating lead source performance record"""
    lead_quality_score: Optional[float] = 0.0
    engagement_rate: Optional[float] = 0.0
    response_rate: Optional[float] = 0.0
    source_metadata: Optional[Dict[str, Any]] = None


class LeadSourcePerformanceResponse(LeadSourcePerformanceBase):
    """Schema for lead source performance response"""
    id: int
    user_id: int
    lead_quality_score: float
    engagement_rate: float
    response_rate: float
    source_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversionRateData(BaseModel):
    """Schema for conversion rate data point"""
    date: str
    rate: float
    source: str


class ROIData(BaseModel):
    """Schema for ROI data point"""
    source: str
    roi: float
    revenue: float
    cost: float


class PerformanceMetric(BaseModel):
    """Schema for performance metric"""
    label: str
    value: str
    change: float
    trend: str  # 'up', 'down', 'stable'


class AnalyticsSummary(BaseModel):
    """Schema for analytics summary dashboard"""
    metrics: List[PerformanceMetric]
    conversion_rates: List[ConversionRateData]
    roi_data: List[ROIData]
    source_distribution: Dict[str, int]
    trend_data: List[Dict[str, Any]]
    period: str  # 'day', 'week', 'month', 'year'