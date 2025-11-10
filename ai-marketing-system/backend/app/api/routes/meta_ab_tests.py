"""
Meta (Facebook/Instagram) A/B Testing API Routes
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.meta_ab_test import MetaABTest, MetaABTestVariant, MetaABTestResult
from app.schemas.meta_ab_test import (
    MetaABTestCreate,
    MetaABTestUpdate,
    MetaABTestResponse,
    MetaABTestVariantResponse,
    MetaABTestAnalysis,
    MetaABTestDeclareWinner,
    MetaABTestStats,
    MetaAdAccountInfo,
    MetaCampaignInfo
)
from app.services.meta_experiments_service import meta_experiments_service

router = APIRouter()


@router.get("/verify-account/{ad_account_id}", response_model=MetaAdAccountInfo)
async def verify_ad_account(
    ad_account_id: str,
    current_user: User = Depends(get_current_user)
):
    """Verify access to a Meta ad account"""
    result = await meta_experiments_service.verify_ad_account(ad_account_id)

    if not result.get("verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to verify ad account")
        )

    return result["account"]


@router.get("/", response_model=List[MetaABTestResponse])
async def get_meta_ab_tests(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all Meta A/B tests for the current user"""
    query = db.query(MetaABTest).filter(MetaABTest.user_id == current_user.id)

    if platform:
        query = query.filter(MetaABTest.platform == platform)

    if status:
        query = query.filter(MetaABTest.status == status)

    tests = query.order_by(desc(MetaABTest.created_at)).offset(skip).limit(limit).all()
    return tests


@router.get("/stats", response_model=MetaABTestStats)
async def get_meta_ab_test_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Meta A/B testing statistics"""
    # Get all tests for the user
    tests = db.query(MetaABTest).filter(MetaABTest.user_id == current_user.id).all()

    total_tests = len(tests)
    running_tests = sum(1 for t in tests if t.status == "running")
    completed_tests = sum(1 for t in tests if t.status == "completed")

    # Calculate total spend
    variants = db.query(MetaABTestVariant).join(MetaABTest).filter(
        MetaABTest.user_id == current_user.id
    ).all()
    total_spend = sum(v.spend for v in variants)

    # Calculate average improvement for completed tests
    improvements = []
    for test in tests:
        if test.status == "completed" and test.winner_variant_id:
            analysis = meta_experiments_service.analyze_experiment(db, test.id)
            if analysis.get("improvement_percentage"):
                improvements.append(analysis["improvement_percentage"])

    avg_improvement = sum(improvements) / len(improvements) if improvements else None

    # Platform breakdown
    platform_breakdown = {
        "facebook": sum(1 for t in tests if t.platform == "facebook"),
        "instagram": sum(1 for t in tests if t.platform == "instagram"),
        "both": sum(1 for t in tests if t.platform == "both")
    }

    return {
        "total_tests": total_tests,
        "running_tests": running_tests,
        "completed_tests": completed_tests,
        "total_spend": total_spend,
        "average_improvement": avg_improvement,
        "platform_breakdown": platform_breakdown
    }


@router.get("/{test_id}", response_model=MetaABTestResponse)
async def get_meta_ab_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific Meta A/B test"""
    test = db.query(MetaABTest).filter(
        MetaABTest.id == test_id,
        MetaABTest.user_id == current_user.id
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta A/B test not found"
        )

    return test


@router.get("/{test_id}/analysis", response_model=MetaABTestAnalysis)
async def get_test_analysis(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analysis of a Meta A/B test"""
    test = db.query(MetaABTest).filter(
        MetaABTest.id == test_id,
        MetaABTest.user_id == current_user.id
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta A/B test not found"
        )

    # Fetch latest results from Meta
    if test.status == "running":
        await meta_experiments_service.fetch_experiment_results(db, test_id)

    # Get analysis
    analysis = meta_experiments_service.analyze_experiment(db, test_id)

    # Add time-series data
    results = db.query(MetaABTestResult).filter(
        MetaABTestResult.test_id == test_id
    ).order_by(MetaABTestResult.date).all()

    performance_over_time = []
    for result in results:
        performance_over_time.append({
            "date": result.date.isoformat(),
            "variant_id": result.variant_id,
            "impressions": result.impressions,
            "clicks": result.clicks,
            "conversions": result.conversions,
            "spend": result.spend,
            "ctr": result.ctr,
            "conversion_rate": result.conversion_rate
        })

    analysis["performance_over_time"] = performance_over_time

    return analysis


@router.post("/", response_model=MetaABTestResponse)
async def create_meta_ab_test(
    test_data: MetaABTestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new Meta A/B test"""
    # Verify ad account
    account_result = await meta_experiments_service.verify_ad_account(test_data.ad_account_id)

    if not account_result.get("verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inaccessible ad account"
        )

    # Create test
    db_test = MetaABTest(
        user_id=current_user.id,
        name=test_data.name,
        description=test_data.description,
        ad_account_id=test_data.ad_account_id,
        platform=test_data.platform,
        test_type=test_data.test_type,
        budget_per_variant=test_data.budget_per_variant,
        duration_days=test_data.duration_days,
        target_audience=test_data.target_audience,
        success_metric=test_data.success_metric,
        scheduled_start=test_data.scheduled_start,
        status="draft"
    )

    db.add(db_test)
    db.commit()
    db.refresh(db_test)

    # Create variants
    variants = []
    for variant_data in test_data.variants:
        db_variant = MetaABTestVariant(
            test_id=db_test.id,
            **variant_data.dict()
        )
        db.add(db_variant)
        variants.append(db_variant)

    db.commit()

    # Create Meta experiment in background
    background_tasks.add_task(
        create_meta_experiment_task,
        db_test.id,
        db
    )

    db.refresh(db_test)
    return db_test


async def create_meta_experiment_task(test_id: int, db: Session):
    """Background task to create Meta experiment"""
    test = db.query(MetaABTest).filter(MetaABTest.id == test_id).first()
    if not test:
        return

    variants = db.query(MetaABTestVariant).filter(
        MetaABTestVariant.test_id == test_id
    ).all()

    result = await meta_experiments_service.create_experiment(db, test, variants)

    if not result.get("success"):
        test.status = "failed"
        db.commit()


@router.put("/{test_id}", response_model=MetaABTestResponse)
async def update_meta_ab_test(
    test_id: int,
    test_update: MetaABTestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a Meta A/B test"""
    test = db.query(MetaABTest).filter(
        MetaABTest.id == test_id,
        MetaABTest.user_id == current_user.id
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta A/B test not found"
        )

    # Only allow updates for draft tests
    if test.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update draft tests"
        )

    # Update fields
    update_data = test_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test, field, value)

    test.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(test)

    return test


@router.post("/{test_id}/start", response_model=MetaABTestResponse)
async def start_meta_ab_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a Meta A/B test"""
    test = db.query(MetaABTest).filter(
        MetaABTest.id == test_id,
        MetaABTest.user_id == current_user.id
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta A/B test not found"
        )

    if test.status != "draft" and test.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test must be in draft or paused status"
        )

    result = await meta_experiments_service.start_experiment(db, test_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to start experiment")
        )

    db.refresh(test)
    return test


@router.post("/{test_id}/pause", response_model=MetaABTestResponse)
async def pause_meta_ab_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pause a Meta A/B test"""
    test = db.query(MetaABTest).filter(
        MetaABTest.id == test_id,
        MetaABTest.user_id == current_user.id
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta A/B test not found"
        )

    if test.status != "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only pause running tests"
        )

    result = await meta_experiments_service.pause_experiment(db, test_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to pause experiment")
        )

    db.refresh(test)
    return test


@router.post("/{test_id}/refresh-results")
async def refresh_test_results(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually refresh test results from Meta"""
    test = db.query(MetaABTest).filter(
        MetaABTest.id == test_id,
        MetaABTest.user_id == current_user.id
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta A/B test not found"
        )

    result = await meta_experiments_service.fetch_experiment_results(db, test_id)

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to fetch results")
        )

    return result["results"]


@router.post("/{test_id}/declare-winner", response_model=MetaABTestResponse)
async def declare_winner(
    test_id: int,
    winner_data: MetaABTestDeclareWinner,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually declare a winner for the test"""
    test = db.query(MetaABTest).filter(
        MetaABTest.id == test_id,
        MetaABTest.user_id == current_user.id
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta A/B test not found"
        )

    # Verify variant belongs to this test
    variant = db.query(MetaABTestVariant).filter(
        MetaABTestVariant.id == winner_data.winner_variant_id,
        MetaABTestVariant.test_id == test_id
    ).first()

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid variant ID"
        )

    # Update test
    test.winner_variant_id = winner_data.winner_variant_id

    if winner_data.end_test:
        test.status = "completed"
        test.ended_at = datetime.utcnow()

    # Update variant
    variant.is_winner = True

    # Update other variants
    other_variants = db.query(MetaABTestVariant).filter(
        MetaABTestVariant.test_id == test_id,
        MetaABTestVariant.id != winner_data.winner_variant_id
    ).all()

    for v in other_variants:
        v.is_winner = False

    db.commit()

    # If apply winner to campaign, pause other variants (implementation needed)
    if winner_data.apply_winner_to_campaign and test.campaign_id:
        # This would pause the losing ad sets and scale the winning one
        pass

    db.refresh(test)
    return test


@router.delete("/{test_id}")
async def delete_meta_ab_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a Meta A/B test"""
    test = db.query(MetaABTest).filter(
        MetaABTest.id == test_id,
        MetaABTest.user_id == current_user.id
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta A/B test not found"
        )

    # Only allow deletion of draft or completed tests
    if test.status not in ["draft", "completed", "failed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active tests"
        )

    db.delete(test)
    db.commit()

    return {"message": "Meta A/B test deleted successfully"}