"""
Meta (Facebook/Instagram) A/B Testing Schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MetaPlatform(str, Enum):
    """Platforms for Meta A/B testing"""
    facebook = "facebook"
    instagram = "instagram"
    both = "both"


class MetaTestType(str, Enum):
    """Types of Meta A/B tests"""
    ad_creative = "ad_creative"
    audience = "audience"
    placement = "placement"
    budget = "budget"
    bidding = "bidding"


class MetaTestStatus(str, Enum):
    """Status of Meta A/B test"""
    draft = "draft"
    scheduled = "scheduled"
    running = "running"
    paused = "paused"
    completed = "completed"
    failed = "failed"


class MetaABTestVariantBase(BaseModel):
    """Base schema for Meta A/B test variant"""
    name: str
    description: Optional[str] = None

    # Creative content
    headline: Optional[str] = None
    primary_text: Optional[str] = None
    description_text: Optional[str] = None
    call_to_action: Optional[str] = None
    link_url: Optional[str] = None

    # Media
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    carousel_items: Optional[List[Dict[str, Any]]] = None

    # Overrides
    audience_override: Optional[Dict[str, Any]] = None
    placement_override: Optional[List[str]] = None
    budget_override: Optional[float] = None
    bid_strategy_override: Optional[str] = None


class MetaABTestVariantCreate(MetaABTestVariantBase):
    """Schema for creating a Meta A/B test variant"""
    pass


class MetaABTestVariantUpdate(BaseModel):
    """Schema for updating a Meta A/B test variant"""
    name: Optional[str] = None
    description: Optional[str] = None
    headline: Optional[str] = None
    primary_text: Optional[str] = None
    description_text: Optional[str] = None
    call_to_action: Optional[str] = None
    link_url: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class MetaABTestVariantResponse(MetaABTestVariantBase):
    """Schema for Meta A/B test variant response"""
    id: int
    test_id: int

    # Performance metrics
    impressions: int
    reach: int
    clicks: int
    conversions: int
    spend: float
    cpm: float
    cpc: float
    ctr: float
    conversion_rate: float
    roas: float

    # Meta IDs
    ad_set_id: Optional[str] = None
    ad_id: Optional[str] = None

    # Status
    is_winner: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MetaABTestBase(BaseModel):
    """Base schema for Meta A/B test"""
    name: str
    description: Optional[str] = None
    ad_account_id: str
    platform: MetaPlatform = MetaPlatform.both
    test_type: MetaTestType

    # Test configuration
    budget_per_variant: float = Field(default=50.0, gt=0)
    duration_days: int = Field(default=7, gt=0, le=30)
    target_audience: Dict[str, Any]
    success_metric: str = "ctr"

    # Scheduling
    scheduled_start: Optional[datetime] = None


class MetaABTestCreate(MetaABTestBase):
    """Schema for creating a Meta A/B test"""
    variants: List[MetaABTestVariantCreate] = Field(..., min_items=2, max_items=5)


class MetaABTestUpdate(BaseModel):
    """Schema for updating a Meta A/B test"""
    name: Optional[str] = None
    description: Optional[str] = None
    budget_per_variant: Optional[float] = None
    duration_days: Optional[int] = None
    target_audience: Optional[Dict[str, Any]] = None
    success_metric: Optional[str] = None
    scheduled_start: Optional[datetime] = None


class MetaABTestResponse(MetaABTestBase):
    """Schema for Meta A/B test response"""
    id: int
    user_id: int
    campaign_id: Optional[str] = None
    status: MetaTestStatus
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    winner_variant_id: Optional[int] = None
    confidence_level: Optional[float] = None
    meta_experiment_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Include variants
    variants: List[MetaABTestVariantResponse] = []

    class Config:
        from_attributes = True


class MetaABTestResultBase(BaseModel):
    """Base schema for Meta A/B test result"""
    date: datetime
    hour: Optional[int] = None
    impressions: int
    reach: int
    clicks: int
    conversions: int
    spend: float
    cpm: float
    cpc: float
    ctr: float
    conversion_rate: float
    demographic_data: Optional[Dict[str, Any]] = None


class MetaABTestResultResponse(MetaABTestResultBase):
    """Schema for Meta A/B test result response"""
    id: int
    test_id: int
    variant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MetaABTestAnalysis(BaseModel):
    """Schema for Meta A/B test analysis"""
    test_id: int
    total_impressions: int
    total_spend: float
    winner_variant_id: Optional[int] = None
    winner_variant_name: Optional[str] = None
    confidence_level: float
    improvement_percentage: float

    # Per-variant analysis
    variant_performance: List[Dict[str, Any]]

    # Time-series data
    performance_over_time: List[Dict[str, Any]]

    # Recommendations
    recommendations: List[str]
    statistical_significance: bool


class MetaABTestDeclareWinner(BaseModel):
    """Schema for declaring a winner"""
    winner_variant_id: int
    apply_winner_to_campaign: bool = False
    end_test: bool = True


class MetaABTestStats(BaseModel):
    """Schema for Meta A/B testing statistics"""
    total_tests: int
    running_tests: int
    completed_tests: int
    total_spend: float
    average_improvement: Optional[float] = None
    best_performing_metric: Optional[str] = None
    platform_breakdown: Dict[str, int]


class MetaAdAccountInfo(BaseModel):
    """Schema for Meta Ad Account information"""
    id: str
    name: str
    currency: str
    account_status: int
    business_name: Optional[str] = None
    available_balance: Optional[float] = None


class MetaAudienceTemplate(BaseModel):
    """Schema for Meta audience template"""
    name: str
    description: Optional[str] = None
    targeting: Dict[str, Any]
    estimated_reach: Optional[int] = None


class MetaCampaignInfo(BaseModel):
    """Schema for existing Meta campaign information"""
    id: str
    name: str
    objective: str
    status: str
    daily_budget: Optional[float] = None
    lifetime_budget: Optional[float] = None