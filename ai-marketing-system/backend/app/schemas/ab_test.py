from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# A/B Test Variant Schemas
class ABTestVariantBase(BaseModel):
    name: str = Field(..., description="Variant name (e.g., 'Variant A')")
    description: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    template_id: Optional[int] = None
    sender_name: Optional[str] = None


class ABTestVariantCreate(ABTestVariantBase):
    pass


class ABTestVariantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    template_id: Optional[int] = None
    sender_name: Optional[str] = None


class ABTestVariantMetricsUpdate(BaseModel):
    total_sent: Optional[int] = None
    total_delivered: Optional[int] = None
    total_opened: Optional[int] = None
    total_clicked: Optional[int] = None
    total_converted: Optional[int] = None
    total_bounced: Optional[int] = None
    total_unsubscribed: Optional[int] = None


class ABTestVariantResponse(ABTestVariantBase):
    id: int
    ab_test_id: int
    
    # Metrics
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int
    total_bounced: int
    total_unsubscribed: int
    
    # Rates
    open_rate: float
    click_rate: float
    conversion_rate: float
    bounce_rate: float
    
    is_winner: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# A/B Test Schemas
class ABTestBase(BaseModel):
    name: str = Field(..., description="Test name")
    description: Optional[str] = None
    test_type: str = Field(default="subject_line", description="Type of test: subject_line, content, template, sender_name")
    sample_size_percentage: float = Field(default=20.0, ge=1.0, le=100.0, description="Percentage of leads to test")
    success_metric: str = Field(default="open_rate", description="Metric to optimize: open_rate, click_rate, conversion_rate")
    auto_select_winner: bool = Field(default=True, description="Automatically select winner based on success metric")


class ABTestCreate(ABTestBase):
    campaign_id: int
    variants: List[ABTestVariantCreate] = Field(..., min_items=2, max_items=5, description="2-5 test variants")


class ABTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    test_type: Optional[str] = None
    sample_size_percentage: Optional[float] = Field(None, ge=1.0, le=100.0)
    success_metric: Optional[str] = None
    auto_select_winner: Optional[bool] = None
    status: Optional[str] = None


class ABTestResponse(ABTestBase):
    id: int
    campaign_id: int
    status: str
    winner_variant_id: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    variants: List[ABTestVariantResponse] = []

    class Config:
        from_attributes = True


class ABTestWithResults(ABTestResponse):
    """Extended response with analysis results"""
    total_test_recipients: int = 0
    best_performing_variant_id: Optional[int] = None
    statistical_significance: Optional[float] = None
    recommended_winner: Optional[int] = None


class ABTestStats(BaseModel):
    """Statistics about A/B tests"""
    total_tests: int = 0
    running_tests: int = 0
    completed_tests: int = 0
    total_variants_tested: int = 0
    average_improvement: Optional[float] = None


class DeclareWinnerRequest(BaseModel):
    """Request to manually declare a winner"""
    winner_variant_id: int
    send_to_remaining: bool = Field(default=True, description="Send winning variant to remaining leads")

