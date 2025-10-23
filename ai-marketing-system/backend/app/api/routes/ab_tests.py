from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ...db.session import get_db
from ...models.ab_test import ABTest, ABTestVariant
from ...models.campaign import Campaign
from ...schemas.ab_test import (
    ABTestCreate,
    ABTestUpdate,
    ABTestResponse,
    ABTestWithResults,
    ABTestStats,
    DeclareWinnerRequest,
    ABTestVariantUpdate,
    ABTestVariantMetricsUpdate,
    ABTestVariantResponse
)
from ...services import ab_test_service
from ...services.email_service import EmailService
from ...services.template_service import TemplateRenderService

router = APIRouter()
email_service = EmailService()
template_service = TemplateRenderService()


@router.post("/", response_model=ABTestResponse, status_code=status.HTTP_201_CREATED)
async def create_ab_test(
    ab_test_data: ABTestCreate,
    db: Session = Depends(get_db)
):
    """Create a new A/B test for a campaign"""
    
    # Verify campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == ab_test_data.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Validate test type
    valid_test_types = ["subject_line", "content", "template", "sender_name"]
    if ab_test_data.test_type not in valid_test_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid test_type. Must be one of: {', '.join(valid_test_types)}"
        )
    
    # Validate success metric
    valid_metrics = ["open_rate", "click_rate", "conversion_rate"]
    if ab_test_data.success_metric not in valid_metrics:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid success_metric. Must be one of: {', '.join(valid_metrics)}"
        )
    
    # Create A/B test
    ab_test = ABTest(
        name=ab_test_data.name,
        description=ab_test_data.description,
        campaign_id=ab_test_data.campaign_id,
        test_type=ab_test_data.test_type,
        sample_size_percentage=ab_test_data.sample_size_percentage,
        success_metric=ab_test_data.success_metric,
        auto_select_winner=ab_test_data.auto_select_winner,
        status="draft"
    )
    
    db.add(ab_test)
    db.commit()
    db.refresh(ab_test)
    
    # Create variants
    for variant_data in ab_test_data.variants:
        variant = ABTestVariant(
            ab_test_id=ab_test.id,
            name=variant_data.name,
            description=variant_data.description,
            subject=variant_data.subject,
            content=variant_data.content,
            template_id=variant_data.template_id,
            sender_name=variant_data.sender_name
        )
        db.add(variant)
    
    db.commit()
    db.refresh(ab_test)
    
    return ab_test


@router.get("/", response_model=List[ABTestResponse])
async def list_ab_tests(
    campaign_id: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all A/B tests with optional filters"""
    query = db.query(ABTest)
    
    if campaign_id:
        query = query.filter(ABTest.campaign_id == campaign_id)
    
    if status:
        query = query.filter(ABTest.status == status)
    
    tests = query.order_by(ABTest.created_at.desc()).offset(skip).limit(limit).all()
    return tests


@router.get("/stats", response_model=ABTestStats)
async def get_ab_test_stats(db: Session = Depends(get_db)):
    """Get A/B testing statistics"""
    total_tests = db.query(ABTest).count()
    running_tests = db.query(ABTest).filter(ABTest.status == "running").count()
    completed_tests = db.query(ABTest).filter(ABTest.status == "completed").count()
    total_variants = db.query(ABTestVariant).count()
    
    # Calculate average improvement (simplified)
    completed = db.query(ABTest).filter(ABTest.status == "completed").all()
    improvements = []
    
    for test in completed:
        if test.winner_variant_id:
            winner = db.query(ABTestVariant).filter(
                ABTestVariant.id == test.winner_variant_id
            ).first()
            
            # Compare with average of other variants
            other_variants = db.query(ABTestVariant).filter(
                ABTestVariant.ab_test_id == test.id,
                ABTestVariant.id != test.winner_variant_id
            ).all()
            
            if winner and other_variants:
                metric_attr = {
                    "open_rate": "open_rate",
                    "click_rate": "click_rate",
                    "conversion_rate": "conversion_rate"
                }.get(test.success_metric, "open_rate")
                
                winner_score = getattr(winner, metric_attr, 0)
                avg_other = sum(getattr(v, metric_attr, 0) for v in other_variants) / len(other_variants)
                
                if avg_other > 0:
                    improvement = ((winner_score - avg_other) / avg_other) * 100
                    improvements.append(improvement)
    
    avg_improvement = sum(improvements) / len(improvements) if improvements else None
    
    return {
        "total_tests": total_tests,
        "running_tests": running_tests,
        "completed_tests": completed_tests,
        "total_variants_tested": total_variants,
        "average_improvement": avg_improvement
    }


@router.get("/{ab_test_id}", response_model=ABTestResponse)
async def get_ab_test(ab_test_id: int, db: Session = Depends(get_db)):
    """Get a specific A/B test"""
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    return ab_test


@router.get("/{ab_test_id}/results", response_model=ABTestWithResults)
async def get_ab_test_results(ab_test_id: int, db: Session = Depends(get_db)):
    """Get A/B test results with analysis"""
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    # Get analysis
    analysis = ab_test_service.analyze_test_results(db, ab_test_id)
    
    # Combine with test data
    response_data = {
        **ab_test.__dict__,
        **analysis
    }
    
    return response_data


@router.put("/{ab_test_id}", response_model=ABTestResponse)
async def update_ab_test(
    ab_test_id: int,
    ab_test_data: ABTestUpdate,
    db: Session = Depends(get_db)
):
    """Update an A/B test"""
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    # Don't allow updates to running/completed tests
    if ab_test.status in ["running", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update test with status '{ab_test.status}'"
        )
    
    # Update fields
    update_data = ab_test_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ab_test, field, value)
    
    ab_test.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ab_test)
    
    return ab_test


@router.delete("/{ab_test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ab_test(ab_test_id: int, db: Session = Depends(get_db)):
    """Delete an A/B test"""
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    # Don't allow deletion of running tests
    if ab_test.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a running test"
        )
    
    # Delete variants first
    db.query(ABTestVariant).filter(ABTestVariant.ab_test_id == ab_test_id).delete()
    
    # Delete test
    db.delete(ab_test)
    db.commit()
    
    return None


@router.post("/{ab_test_id}/start", response_model=ABTestResponse)
async def start_ab_test(
    ab_test_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start running an A/B test"""
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    if ab_test.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test must be in draft status to start"
        )
    
    # Verify we have variants
    variants = db.query(ABTestVariant).filter(
        ABTestVariant.ab_test_id == ab_test_id
    ).all()
    
    if len(variants) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test must have at least 2 variants"
        )
    
    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == ab_test.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update test status
    ab_test.status = "running"
    ab_test.started_at = datetime.utcnow()
    db.commit()
    db.refresh(ab_test)
    
    # Split leads and send in background
    background_tasks.add_task(send_ab_test_emails, ab_test_id, db)
    
    return ab_test


def send_ab_test_emails(ab_test_id: int, db: Session):
    """Background task to send A/B test emails"""
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        return
    
    campaign = db.query(Campaign).filter(Campaign.id == ab_test.campaign_id).first()
    if not campaign:
        return
    
    # Split leads
    variant_assignments = ab_test_service.split_leads_for_test(db, ab_test, campaign)
    
    # Send emails for each variant
    for variant_id, leads in variant_assignments.items():
        variant = db.query(ABTestVariant).filter(ABTestVariant.id == variant_id).first()
        if not variant:
            continue
        
        # Prepare email content
        if variant.template_id:
            # Use template
            from ...models.email_template import EmailTemplate
            template = db.query(EmailTemplate).filter(
                EmailTemplate.id == variant.template_id
            ).first()
            
            if template:
                for lead in leads:
                    variables = template_service.prepare_variables(lead.__dict__)
                    subject = template_service.render_template(template.subject, variables)
                    content = template_service.render_template(template.html_content, variables)
                    
                    try:
                        email_service.send_email(
                            to_email=lead.email,
                            subject=subject,
                            html_content=content
                        )
                        variant.total_sent += 1
                        variant.total_delivered += 1
                    except Exception as e:
                        print(f"Error sending email: {e}")
        else:
            # Use custom content
            for lead in leads:
                subject = variant.subject or campaign.subject
                content = variant.content or campaign.content
                
                # Wrap in email template
                html_content = email_service.create_email_template(content)
                
                try:
                    email_service.send_email(
                        to_email=lead.email,
                        subject=subject,
                        html_content=html_content
                    )
                    variant.total_sent += 1
                    variant.total_delivered += 1
                except Exception as e:
                    print(f"Error sending email: {e}")
        
        # Update variant metrics
        ab_test_service.calculate_variant_metrics(variant)
        db.commit()


@router.post("/{ab_test_id}/declare-winner", response_model=ABTestResponse)
async def declare_test_winner(
    ab_test_id: int,
    winner_request: DeclareWinnerRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually declare a winner for the A/B test"""
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if not ab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A/B test not found"
        )
    
    if ab_test.status != "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only declare winner for running tests"
        )
    
    # Declare winner
    updated_test = ab_test_service.declare_winner(
        db, ab_test_id, winner_request.winner_variant_id
    )
    
    if not updated_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid winner variant"
        )
    
    # Send to remaining leads if requested
    if winner_request.send_to_remaining:
        background_tasks.add_task(
            send_winner_to_remaining,
            ab_test_id,
            winner_request.winner_variant_id,
            db
        )
    
    return updated_test


def send_winner_to_remaining(ab_test_id: int, winner_variant_id: int, db: Session):
    """Send winning variant to remaining leads"""
    # This is a placeholder - implement based on your email sending logic
    pass


@router.put("/{ab_test_id}/variants/{variant_id}", response_model=ABTestVariantResponse)
async def update_variant(
    ab_test_id: int,
    variant_id: int,
    variant_data: ABTestVariantUpdate,
    db: Session = Depends(get_db)
):
    """Update a test variant"""
    variant = db.query(ABTestVariant).filter(
        ABTestVariant.id == variant_id,
        ABTestVariant.ab_test_id == ab_test_id
    ).first()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )
    
    # Check test status
    ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
    if ab_test.status in ["running", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update variant for running/completed test"
        )
    
    # Update fields
    update_data = variant_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(variant, field, value)
    
    variant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(variant)
    
    return variant


@router.put("/{ab_test_id}/variants/{variant_id}/metrics", response_model=ABTestVariantResponse)
async def update_variant_metrics(
    ab_test_id: int,
    variant_id: int,
    metrics_data: ABTestVariantMetricsUpdate,
    db: Session = Depends(get_db)
):
    """Update variant metrics (for tracking email events)"""
    variant = db.query(ABTestVariant).filter(
        ABTestVariant.id == variant_id,
        ABTestVariant.ab_test_id == ab_test_id
    ).first()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )
    
    # Update metrics
    update_data = metrics_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(variant, field, value)
    
    # Recalculate rates
    ab_test_service.calculate_variant_metrics(variant)
    
    variant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(variant)
    
    # Check if we should auto-select winner
    ab_test_service.auto_select_winner_if_ready(db, ab_test_id)
    
    return variant

