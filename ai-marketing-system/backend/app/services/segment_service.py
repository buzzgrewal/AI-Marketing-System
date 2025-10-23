from typing import List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
from app.models.lead import Lead
from app.models.segment import Segment
from datetime import datetime


class SegmentService:
    """Service for evaluating and managing segments"""
    
    @staticmethod
    def get_available_fields() -> List[Dict[str, Any]]:
        """Get list of available fields for segmentation"""
        return [
            {
                "field": "email",
                "label": "Email",
                "type": "string",
                "operators": ["equals", "not_equals", "contains", "not_contains", "exists", "not_exists"],
                "example_value": "john@example.com"
            },
            {
                "field": "first_name",
                "label": "First Name",
                "type": "string",
                "operators": ["equals", "not_equals", "contains", "not_contains", "exists", "not_exists"],
                "example_value": "John"
            },
            {
                "field": "last_name",
                "label": "Last Name",
                "type": "string",
                "operators": ["equals", "not_equals", "contains", "not_contains", "exists", "not_exists"],
                "example_value": "Doe"
            },
            {
                "field": "phone",
                "label": "Phone",
                "type": "string",
                "operators": ["equals", "not_equals", "contains", "exists", "not_exists"],
                "example_value": "555-0100"
            },
            {
                "field": "location",
                "label": "Location",
                "type": "string",
                "operators": ["equals", "not_equals", "contains", "not_contains", "in", "not_in"],
                "example_value": "California"
            },
            {
                "field": "sport_type",
                "label": "Sport Type",
                "type": "list",
                "operators": ["equals", "not_equals", "in", "not_in"],
                "example_value": ["cycling", "triathlon", "running", "multiple"]
            },
            {
                "field": "customer_type",
                "label": "Customer Type",
                "type": "list",
                "operators": ["equals", "not_equals", "in", "not_in"],
                "example_value": ["athlete", "coach", "team", "bike_fitter"]
            },
            {
                "field": "status",
                "label": "Status",
                "type": "list",
                "operators": ["equals", "not_equals", "in", "not_in"],
                "example_value": ["new", "active", "inactive", "customer"]
            },
            {
                "field": "email_consent",
                "label": "Email Consent",
                "type": "boolean",
                "operators": ["equals"],
                "example_value": True
            },
            {
                "field": "sms_consent",
                "label": "SMS Consent",
                "type": "boolean",
                "operators": ["equals"],
                "example_value": True
            },
            {
                "field": "consent_date",
                "label": "Consent Date",
                "type": "date",
                "operators": ["equals", "not_equals", "greater_than", "less_than", "exists", "not_exists"],
                "example_value": "2024-01-01"
            },
            {
                "field": "created_at",
                "label": "Created Date",
                "type": "date",
                "operators": ["equals", "not_equals", "greater_than", "less_than"],
                "example_value": "2024-01-01"
            },
            {
                "field": "source",
                "label": "Source",
                "type": "string",
                "operators": ["equals", "not_equals", "contains", "in", "not_in"],
                "example_value": "website"
            },
        ]
    
    @staticmethod
    def evaluate_condition(lead: Lead, condition: Dict[str, Any]) -> bool:
        """Evaluate a single condition against a lead"""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        # Get field value from lead
        lead_value = getattr(lead, field, None)
        
        # Handle different operators
        if operator == "equals":
            return lead_value == value
        
        elif operator == "not_equals":
            return lead_value != value
        
        elif operator == "in":
            if not isinstance(value, list):
                value = [value]
            return lead_value in value
        
        elif operator == "not_in":
            if not isinstance(value, list):
                value = [value]
            return lead_value not in value
        
        elif operator == "contains":
            if lead_value is None:
                return False
            return str(value).lower() in str(lead_value).lower()
        
        elif operator == "not_contains":
            if lead_value is None:
                return True
            return str(value).lower() not in str(lead_value).lower()
        
        elif operator == "greater_than":
            if lead_value is None:
                return False
            try:
                return lead_value > value
            except:
                return False
        
        elif operator == "less_than":
            if lead_value is None:
                return False
            try:
                return lead_value < value
            except:
                return False
        
        elif operator == "exists":
            return lead_value is not None and lead_value != ""
        
        elif operator == "not_exists":
            return lead_value is None or lead_value == ""
        
        else:
            return False
    
    @staticmethod
    def evaluate_criteria(lead: Lead, criteria: Dict[str, Any]) -> bool:
        """Evaluate segment criteria against a lead"""
        operator = criteria.get("operator", "AND")
        conditions = criteria.get("conditions", [])
        
        if not conditions:
            return True
        
        results = [SegmentService.evaluate_condition(lead, cond) for cond in conditions]
        
        if operator == "AND":
            return all(results)
        elif operator == "OR":
            return any(results)
        else:
            return False
    
    @staticmethod
    def get_matching_leads(criteria: Dict[str, Any], db: Session, limit: int = None) -> List[Lead]:
        """Get all leads matching the segment criteria"""
        
        # Get all leads
        query = db.query(Lead)
        
        if limit:
            query = query.limit(limit)
        
        all_leads = query.all()
        
        # Filter leads based on criteria
        matching_leads = [
            lead for lead in all_leads
            if SegmentService.evaluate_criteria(lead, criteria)
        ]
        
        return matching_leads
    
    @staticmethod
    def count_matching_leads(criteria: Dict[str, Any], db: Session) -> int:
        """Count leads matching the segment criteria"""
        matching_leads = SegmentService.get_matching_leads(criteria, db)
        return len(matching_leads)
    
    @staticmethod
    def update_segment_count(segment_id: int, db: Session):
        """Update cached lead count for a segment"""
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return
        
        # Count matching leads
        count = SegmentService.count_matching_leads(segment.criteria, db)
        
        # Update segment
        segment.lead_count = count
        segment.last_calculated = datetime.utcnow()
        db.commit()
    
    @staticmethod
    def validate_criteria(criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate segment criteria"""
        errors = []
        warnings = []
        
        operator = criteria.get("operator")
        conditions = criteria.get("conditions", [])
        
        # Validate operator
        if operator not in ["AND", "OR"]:
            errors.append(f"Invalid operator: {operator}. Must be AND or OR")
        
        # Validate conditions
        if not conditions:
            warnings.append("No conditions specified. Segment will match all leads.")
        
        available_fields = {f["field"] for f in SegmentService.get_available_fields()}
        
        for i, condition in enumerate(conditions):
            field = condition.get("field")
            op = condition.get("operator")
            value = condition.get("value")
            
            if not field:
                errors.append(f"Condition {i+1}: Missing field")
                continue
            
            if field not in available_fields:
                errors.append(f"Condition {i+1}: Invalid field '{field}'")
            
            if not op:
                errors.append(f"Condition {i+1}: Missing operator")
            
            if value is None and op not in ["exists", "not_exists"]:
                warnings.append(f"Condition {i+1}: No value specified")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def get_segment_leads(segment_id: int, db: Session, limit: int = None) -> List[Lead]:
        """Get all leads matching a specific segment"""
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return []
        
        return SegmentService.get_matching_leads(segment.criteria, db, limit)


# Singleton instance
segment_service = SegmentService()

