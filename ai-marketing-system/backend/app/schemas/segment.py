from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SegmentCondition(BaseModel):
    """Single condition in a segment"""
    field: str = Field(..., description="Field to filter on (e.g., sport_type, status, email_consent)")
    operator: str = Field(..., description="Comparison operator: equals, not_equals, in, not_in, contains, greater_than, less_than, exists, not_exists")
    value: Any = Field(..., description="Value to compare against")


class SegmentCriteria(BaseModel):
    """Segment criteria with multiple conditions"""
    operator: str = Field(default="AND", description="Logic operator: AND or OR")
    conditions: List[SegmentCondition] = Field(..., description="List of conditions")


class SegmentBase(BaseModel):
    """Base schema for segment"""
    name: str = Field(..., min_length=1, max_length=255, description="Segment name")
    description: Optional[str] = Field(None, description="Segment description")
    criteria: SegmentCriteria = Field(..., description="Segment filter criteria")
    segment_type: str = Field(default="dynamic", description="Segment type: dynamic or static")
    is_active: bool = Field(default=True, description="Whether segment is active")
    tags: Optional[List[str]] = Field(None, description="Tags for organization")


class SegmentCreate(SegmentBase):
    """Schema for creating a segment"""
    pass


class SegmentUpdate(BaseModel):
    """Schema for updating a segment"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    criteria: Optional[SegmentCriteria] = None
    segment_type: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None


class SegmentResponse(SegmentBase):
    """Schema for segment response"""
    id: int
    lead_count: int
    last_calculated: Optional[datetime]
    campaign_count: int
    last_used: Optional[datetime]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SegmentPreviewRequest(BaseModel):
    """Schema for previewing segment matches"""
    criteria: SegmentCriteria
    limit: int = Field(default=10, ge=1, le=100, description="Max leads to return")


class SegmentPreviewResponse(BaseModel):
    """Schema for segment preview response"""
    total_matches: int
    leads: List[Dict[str, Any]]


class SegmentField(BaseModel):
    """Available field for segmentation"""
    field: str
    label: str
    type: str  # string, number, boolean, date, list
    operators: List[str]
    example_value: Optional[Any] = None


class SegmentFieldsResponse(BaseModel):
    """Response with available fields for segmentation"""
    fields: List[SegmentField]


class SegmentStatsResponse(BaseModel):
    """Segment statistics"""
    total_segments: int
    active_segments: int
    total_leads_covered: int
    most_used_segment: Optional[Dict[str, Any]]

