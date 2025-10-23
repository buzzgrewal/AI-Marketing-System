from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.scheduled_post import ScheduledPost
from app.models.content import GeneratedContent
from app.schemas.scheduled_post import (
    ScheduledPostCreate,
    ScheduledPostUpdate,
    ScheduledPostResponse,
    SchedulingCalendarResponse,
    PostMetricsUpdate,
    BulkScheduleRequest,
    ScheduleFromContentRequest
)
from app.services.social_scheduler import social_scheduler

router = APIRouter()


@router.post("/", response_model=ScheduledPostResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_post(
    post_data: ScheduledPostCreate,
    db: Session = Depends(get_db)
):
    """Schedule a new social media post"""
    
    # Validate post content for platform
    validation = social_scheduler.validate_post_content(
        post_data.platform,
        post_data.post_text,
        post_data.image_url
    )
    
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {', '.join(validation['errors'])}"
        )
    
    # Create scheduled post
    new_post = ScheduledPost(
        **post_data.model_dump(),
        created_by=None,
        status="scheduled"
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post


@router.post("/from-content", response_model=ScheduledPostResponse)
async def schedule_from_content(
    request: ScheduleFromContentRequest,
    db: Session = Depends(get_db)
):
    """Schedule a post from existing generated content"""
    
    # Get the content
    content = db.query(GeneratedContent).filter(GeneratedContent.id == request.content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Validate
    validation = social_scheduler.validate_post_content(
        content.platform,
        content.caption or content.body,
        content.image_url
    )
    
    if not validation['valid']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content validation failed: {', '.join(validation['errors'])}"
        )
    
    # Create scheduled post from content
    new_post = ScheduledPost(
        content_id=content.id,
        platform=content.platform,
        post_text=content.caption or content.body,
        image_url=content.image_url,
        hashtags=content.hashtags,
        scheduled_time=request.scheduled_time,
        timezone=request.timezone,
        auto_post=request.auto_post,
        platform_settings=request.platform_settings,
        created_by=None,
        status="scheduled"
    )
    
    db.add(new_post)
    
    # Update content status
    content.status = "scheduled"
    
    db.commit()
    db.refresh(new_post)
    
    return new_post


@router.post("/bulk", response_model=List[ScheduledPostResponse])
async def bulk_schedule_posts(
    request: BulkScheduleRequest,
    db: Session = Depends(get_db)
):
    """Schedule multiple posts at once"""
    
    created_posts = []
    errors = []
    
    for post_data in request.posts:
        try:
            # Validate
            validation = social_scheduler.validate_post_content(
                post_data.platform,
                post_data.post_text,
                post_data.image_url
            )
            
            if not validation['valid']:
                errors.append(f"Post validation failed: {', '.join(validation['errors'])}")
                continue
            
            # Create
            new_post = ScheduledPost(
                **post_data.model_dump(),
                created_by=None,
                status="scheduled"
            )
            
            db.add(new_post)
            created_posts.append(new_post)
            
        except Exception as e:
            errors.append(f"Error creating post: {str(e)}")
    
    db.commit()
    
    for post in created_posts:
        db.refresh(post)
    
    if errors:
        print(f"Bulk schedule had errors: {errors}")
    
    return created_posts


@router.get("/", response_model=List[ScheduledPostResponse])
async def get_scheduled_posts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get all scheduled posts with optional filters"""
    
    query = db.query(ScheduledPost)
    
    # Apply filters
    if status:
        query = query.filter(ScheduledPost.status == status)
    
    if platform:
        query = query.filter(ScheduledPost.platform == platform)
    
    if start_date:
        query = query.filter(ScheduledPost.scheduled_time >= start_date)
    
    if end_date:
        query = query.filter(ScheduledPost.scheduled_time <= end_date)
    
    posts = query.order_by(ScheduledPost.scheduled_time.asc()).offset(skip).limit(limit).all()
    return posts


@router.get("/calendar", response_model=List[SchedulingCalendarResponse])
async def get_calendar_view(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get posts organized by date for calendar view"""
    
    # Default to current month if no dates provided
    if not start_date:
        start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if not end_date:
        # End of month
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1)
    
    # Get posts in date range
    posts = db.query(ScheduledPost).filter(
        and_(
            ScheduledPost.scheduled_time >= start_date,
            ScheduledPost.scheduled_time < end_date
        )
    ).order_by(ScheduledPost.scheduled_time.asc()).all()
    
    # Group by date
    posts_by_date = {}
    for post in posts:
        date_key = post.scheduled_time.strftime("%Y-%m-%d")
        if date_key not in posts_by_date:
            posts_by_date[date_key] = []
        posts_by_date[date_key].append(post)
    
    # Format response
    calendar_data = [
        SchedulingCalendarResponse(date=date, posts=posts)
        for date, posts in sorted(posts_by_date.items())
    ]
    
    return calendar_data


@router.get("/{post_id}", response_model=ScheduledPostResponse)
async def get_scheduled_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific scheduled post"""
    
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    return post


@router.put("/{post_id}", response_model=ScheduledPostResponse)
async def update_scheduled_post(
    post_id: int,
    post_data: ScheduledPostUpdate,
    db: Session = Depends(get_db)
):
    """Update a scheduled post"""
    
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    # Don't allow updating posted or posting posts
    if post.status in ["posted", "posting"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update posts that are posted or currently posting"
        )
    
    # Update fields
    update_dict = post_data.model_dump(exclude_unset=True)
    
    # Validate if content is being updated
    if 'post_text' in update_dict or 'platform' in update_dict:
        validation = social_scheduler.validate_post_content(
            update_dict.get('platform', post.platform),
            update_dict.get('post_text', post.post_text),
            update_dict.get('image_url', post.image_url)
        )
        
        if not validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {', '.join(validation['errors'])}"
            )
    
    for field, value in update_dict.items():
        setattr(post, field, value)
    
    post.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(post)
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduled_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Delete/cancel a scheduled post"""
    
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    # Can't delete posted posts, only cancel scheduled ones
    if post.status == "posted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete posted content. Posted content is archived."
        )
    
    # If scheduled, mark as cancelled instead of deleting
    if post.status == "scheduled":
        post.status = "cancelled"
        db.commit()
    else:
        db.delete(post)
        db.commit()
    
    return None


@router.post("/{post_id}/post-now", response_model=ScheduledPostResponse)
async def post_now(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Immediately post a scheduled item (override schedule)"""
    
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    if post.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only post scheduled posts. Current status: {post.status}"
        )
    
    # Update status
    post.status = "posting"
    db.commit()
    
    # Post in background
    background_tasks.add_task(post_scheduled_item, post.id, db)
    
    db.refresh(post)
    return post


async def post_scheduled_item(post_id: int, db: Session):
    """Background task to post an item"""
    
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        return
    
    try:
        result = await social_scheduler.post_to_platform(post, db)
        
        if result['success']:
            post.status = "posted"
            post.posted_at = datetime.utcnow()
            post.platform_post_id = result.get('post_id')
            post.platform_url = result.get('post_url')
        else:
            post.status = "failed"
            post.error_message = result.get('error')
        
        db.commit()
        
    except Exception as e:
        post.status = "failed"
        post.error_message = str(e)
        db.commit()


@router.post("/{post_id}/metrics/refresh")
async def refresh_metrics(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Refresh engagement metrics for a posted item"""
    
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    if post.status != "posted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only refresh metrics for posted content"
        )
    
    await social_scheduler.update_post_metrics(post, db)
    
    return {
        "message": "Metrics updated",
        "likes": post.likes_count,
        "comments": post.comments_count,
        "shares": post.shares_count,
        "reach": post.reach,
        "engagement_rate": post.engagement_rate
    }


@router.get("/stats/overview")
async def get_scheduling_stats(
    db: Session = Depends(get_db)
):
    """Get overview statistics for scheduled posts"""
    
    total_scheduled = db.query(ScheduledPost).filter(ScheduledPost.status == "scheduled").count()
    total_posted = db.query(ScheduledPost).filter(ScheduledPost.status == "posted").count()
    total_failed = db.query(ScheduledPost).filter(ScheduledPost.status == "failed").count()
    
    # Posts in next 7 days
    next_week = datetime.utcnow() + timedelta(days=7)
    upcoming = db.query(ScheduledPost).filter(
        and_(
            ScheduledPost.status == "scheduled",
            ScheduledPost.scheduled_time <= next_week
        )
    ).count()
    
    # Average engagement for posted content
    posted_posts = db.query(ScheduledPost).filter(ScheduledPost.status == "posted").all()
    avg_engagement = 0
    if posted_posts:
        total_engagement = sum(p.engagement_rate for p in posted_posts)
        avg_engagement = total_engagement / len(posted_posts)
    
    return {
        "total_scheduled": total_scheduled,
        "total_posted": total_posted,
        "total_failed": total_failed,
        "upcoming_week": upcoming,
        "avg_engagement_rate": round(avg_engagement, 2)
    }


@router.get("/platforms/status")
async def get_platforms_status():
    """Get status of social media platform integrations"""
    
    platforms = [
        {
            "name": "Facebook",
            "key": "facebook",
            "enabled": bool(social_scheduler.platforms_config['facebook']['enabled']),
            "features": ["posts", "images", "links"]
        },
        {
            "name": "Instagram",
            "key": "instagram",
            "enabled": bool(social_scheduler.platforms_config['instagram']['enabled']),
            "features": ["posts", "images", "required_image"]
        },
        {
            "name": "Twitter",
            "key": "twitter",
            "enabled": bool(social_scheduler.platforms_config['twitter']['enabled']),
            "features": ["posts", "images", "280_char_limit"]
        },
        {
            "name": "LinkedIn",
            "key": "linkedin",
            "enabled": bool(social_scheduler.platforms_config['linkedin']['enabled']),
            "features": ["posts", "images", "articles"]
        }
    ]
    
    return {"platforms": platforms}

