from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import random
from ..models.ab_test import ABTest, ABTestVariant
from ..models.lead import Lead
from ..models.campaign import Campaign
from ..models.segment import Segment
from ..services.segment_service import SegmentService


def split_leads_for_test(
    db: Session,
    ab_test: ABTest,
    campaign: Campaign
) -> Dict[int, List[Lead]]:
    """
    Split leads into groups for A/B testing
    
    Returns a dict mapping variant_id -> list of leads
    """
    # Get all targeted leads based on campaign settings
    if campaign.segment_id:
        # Use segment to get leads
        segment = db.query(Segment).filter(Segment.id == campaign.segment_id).first()
        if segment:
            all_leads = SegmentService.get_segment_leads(campaign.segment_id, db)
        else:
            all_leads = []
    else:
        # Use traditional filters
        query = db.query(Lead).filter(Lead.email_consent == True)
        if campaign.target_sport_type:
            query = query.filter(Lead.sport_type == campaign.target_sport_type)
        all_leads = query.all()
    
    if not all_leads:
        return {}
    
    # Calculate test sample size
    total_leads = len(all_leads)
    test_sample_size = int(total_leads * (ab_test.sample_size_percentage / 100.0))
    
    # Select random sample for testing
    test_leads = random.sample(all_leads, min(test_sample_size, total_leads))
    
    # Get variants
    variants = db.query(ABTestVariant).filter(
        ABTestVariant.ab_test_id == ab_test.id
    ).all()
    
    if not variants:
        return {}
    
    # Split test leads evenly among variants
    variant_assignments = {}
    leads_per_variant = len(test_leads) // len(variants)
    
    for i, variant in enumerate(variants):
        start_idx = i * leads_per_variant
        if i == len(variants) - 1:
            # Last variant gets any remaining leads
            variant_assignments[variant.id] = test_leads[start_idx:]
        else:
            end_idx = start_idx + leads_per_variant
            variant_assignments[variant.id] = test_leads[start_idx:end_idx]
    
    return variant_assignments


def calculate_variant_metrics(variant: ABTestVariant) -> None:
    """Calculate performance metrics for a variant"""
    if variant.total_sent > 0:
        variant.open_rate = (variant.total_opened / variant.total_sent) * 100
        variant.click_rate = (variant.total_clicked / variant.total_sent) * 100
        variant.conversion_rate = (variant.total_converted / variant.total_sent) * 100
        variant.bounce_rate = (variant.total_bounced / variant.total_sent) * 100
    else:
        variant.open_rate = 0.0
        variant.click_rate = 0.0
        variant.conversion_rate = 0.0
        variant.bounce_rate = 0.0


def analyze_test_results(
    db: Session,
    ab_test_id: int
) -> Dict[str, any]:
    """
    Analyze A/B test results and determine the best performing variant
    
    Returns analysis including recommended winner
    """
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        return {}
    
    variants = db.query(ABTestVariant).filter(
        ABTestVariant.ab_test_id == ab_test_id
    ).all()
    
    if not variants:
        return {}
    
    # Recalculate metrics for all variants
    for variant in variants:
        calculate_variant_metrics(variant)
    
    db.commit()
    
    # Determine best performer based on success metric
    metric_map = {
        "open_rate": "open_rate",
        "click_rate": "click_rate",
        "conversion_rate": "conversion_rate"
    }
    
    metric_attr = metric_map.get(ab_test.success_metric, "open_rate")
    
    # Sort variants by the success metric
    sorted_variants = sorted(
        variants,
        key=lambda v: getattr(v, metric_attr, 0),
        reverse=True
    )
    
    best_variant = sorted_variants[0] if sorted_variants else None
    
    # Calculate statistical significance (simplified)
    # In a production system, you'd use proper statistical tests
    if len(sorted_variants) >= 2:
        best_score = getattr(best_variant, metric_attr, 0)
        second_best_score = getattr(sorted_variants[1], metric_attr, 0)
        
        if second_best_score > 0:
            improvement = ((best_score - second_best_score) / second_best_score) * 100
        else:
            improvement = 100.0 if best_score > 0 else 0.0
        
        # Simple significance check: >10% improvement with enough data
        min_samples = 30
        has_enough_data = best_variant.total_sent >= min_samples
        is_significant = improvement > 10.0 and has_enough_data
        
        statistical_significance = improvement if is_significant else 0.0
    else:
        improvement = 0.0
        statistical_significance = 0.0
    
    # Calculate total recipients
    total_test_recipients = sum(v.total_sent for v in variants)
    
    return {
        "total_test_recipients": total_test_recipients,
        "best_performing_variant_id": best_variant.id if best_variant else None,
        "statistical_significance": statistical_significance,
        "recommended_winner": best_variant.id if best_variant and statistical_significance > 0 else None,
        "variants": [
            {
                "id": v.id,
                "name": v.name,
                metric_attr: getattr(v, metric_attr, 0),
                "total_sent": v.total_sent,
                "is_winner": v.is_winner
            }
            for v in sorted_variants
        ]
    }


def declare_winner(
    db: Session,
    ab_test_id: int,
    winner_variant_id: int
) -> ABTest:
    """
    Declare a winning variant for the A/B test
    """
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        return None
    
    # Verify the variant belongs to this test
    winner = db.query(ABTestVariant).filter(
        ABTestVariant.id == winner_variant_id,
        ABTestVariant.ab_test_id == ab_test_id
    ).first()
    
    if not winner:
        return None
    
    # Update test
    ab_test.winner_variant_id = winner_variant_id
    ab_test.status = "completed"
    
    # Update all variants
    variants = db.query(ABTestVariant).filter(
        ABTestVariant.ab_test_id == ab_test_id
    ).all()
    
    for variant in variants:
        variant.is_winner = (variant.id == winner_variant_id)
    
    db.commit()
    db.refresh(ab_test)
    
    return ab_test


def auto_select_winner_if_ready(
    db: Session,
    ab_test_id: int
) -> Optional[ABTest]:
    """
    Automatically select winner if conditions are met
    
    Conditions:
    - Test is running
    - Auto-select is enabled
    - Enough data collected
    - Clear winner exists
    """
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test or not ab_test.auto_select_winner or ab_test.status != "running":
        return None
    
    # Analyze results
    analysis = analyze_test_results(db, ab_test_id)
    
    # Check if we have a recommended winner
    if analysis.get("recommended_winner"):
        # Minimum sample size requirement
        if analysis.get("total_test_recipients", 0) >= 50:
            return declare_winner(db, ab_test_id, analysis["recommended_winner"])
    
    return None


def get_remaining_leads(
    db: Session,
    ab_test: ABTest,
    campaign: Campaign,
    test_lead_ids: List[int]
) -> List[Lead]:
    """
    Get leads that were NOT part of the A/B test
    """
    # Get all targeted leads
    if campaign.segment_id:
        segment = db.query(Segment).filter(Segment.id == campaign.segment_id).first()
        if segment:
            all_leads = SegmentService.get_segment_leads(campaign.segment_id, db)
        else:
            all_leads = []
    else:
        query = db.query(Lead).filter(Lead.email_consent == True)
        if campaign.target_sport_type:
            query = query.filter(Lead.sport_type == campaign.target_sport_type)
        all_leads = query.all()
    
    # Filter out test leads
    remaining_leads = [lead for lead in all_leads if lead.id not in test_lead_ids]
    
    return remaining_leads

