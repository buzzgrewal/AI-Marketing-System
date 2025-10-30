from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from app.db.session import get_db
from app.models.content import GeneratedContent
from app.models.user import User
from app.schemas.content import (
    ContentGenerationRequest,
    ContentResponse,
    ContentUpdateRequest,
    ContentPerformanceUpdate
)
from app.core.security import get_current_active_user
from app.core.config import settings
from app.services.ai_content_generator import ai_content_generator

router = APIRouter()


@router.post("/generate", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def generate_content(
    request: ContentGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate marketing content using AI"""

    try:
        # Generate content based on type
        if request.content_type == "social_post":
            if not request.platform:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Platform is required for social posts"
                )

            ai_result = await ai_content_generator.generate_social_post(
                topic=request.topic,
                platform=request.platform,
                tone=request.tone,
                target_audience=request.target_audience,
                additional_context=request.additional_context
            )

            # Validate AI result
            if not ai_result or not ai_result.get("caption"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate content. AI returned empty result."
                )

            # Generate or enhance image if requested
            image_prompt = None
            image_url = None
            if request.include_image:
                try:
                    if request.product_image_base64:
                        # User provided their own product image - enhance it
                        print(f"Enhancing user's product image for: {request.topic}")
                        
                        # Create enhancement prompt based on topic and style
                        enhancement_instructions = f"""Transform this product image for marketing purposes:
- Topic/Context: {request.topic}
- Style: {request.image_style or 'professional product photography'}
- Target Audience: {request.target_audience}
- Tone: {request.tone}

Enhance the image by:
1. Adding an appropriate background or setting that fits the topic
2. Improving lighting and colors for marketing appeal
3. Adding professional effects or ambiance that matches the tone
4. Making it visually compelling for social media

Keep the product as the main focus while creating an engaging marketing scene around it.
Generate a new enhanced marketing image based on these requirements."""
                        
                        image_prompt = enhancement_instructions
                        image_url = await ai_content_generator.enhance_product_image(
                            product_image_base64=request.product_image_base64,
                            enhancement_prompt=enhancement_instructions,
                            aspect_ratio="1:1"
                        )
                        print(f"Product image enhanced successfully: {image_url}")
                    else:
                        # Generate image from scratch
                        print(f"Generating image prompt for: {request.topic}")
                        image_prompt = await ai_content_generator.generate_image_prompt(
                            content_topic=request.topic,
                            style=request.image_style or "professional product photography"
                        )
                        print(f"Image prompt generated: {image_prompt[:100]}...")

                        # Then generate the actual image
                        print(f"Generating actual image...")
                        image_url = await ai_content_generator.generate_image(
                            prompt=image_prompt,
                            aspect_ratio="1:1"  # 1:1 for square images (1024x1024)
                        )
                        print(f"Image generated successfully: {image_url}")
                except Exception as e:
                    print(f"Failed to generate/enhance image: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Continue without image if generation fails

            # Handle hashtags - could be array or string
            hashtags = ai_result.get("hashtags", "")
            if isinstance(hashtags, list):
                hashtags = " ".join(hashtags)
            
            # Create content record
            new_content = GeneratedContent(
                content_type=request.content_type,
                platform=request.platform,
                title=ai_result.get("title", ""),
                caption=ai_result.get("caption", ""),
                hashtags=hashtags,
                image_prompt=image_prompt,
                image_url=image_url,
                prompt_used=request.topic,
                ai_model=ai_content_generator.text_model,
                created_by=None
            )

        elif request.content_type == "email_template":
            ai_result = await ai_content_generator.generate_email_content(
                subject_topic=request.topic,
                purpose=request.additional_context or "Marketing email",
                tone=request.tone,
                target_audience=request.target_audience
            )

            # Validate AI result
            if not ai_result or not ai_result.get("body"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate email content. AI returned empty result."
                )

            new_content = GeneratedContent(
                content_type=request.content_type,
                platform="email",
                title=ai_result.get("subject", ""),
                caption=ai_result.get("preview_text", ""),
                body=ai_result.get("body", ""),
                prompt_used=request.topic,
                ai_model=ai_content_generator.text_model,
                created_by=None
            )

        elif request.content_type == "ad_copy":
            ai_result = await ai_content_generator.generate_ad_copy(
                product_name=request.topic,
                product_description=request.additional_context or "",
                platform=request.platform or "facebook",
                tone=request.tone,
                target_audience=request.target_audience
            )

            # Validate AI result
            if not ai_result or not ai_result.get("primary_text"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate ad copy. AI returned empty result."
                )

            new_content = GeneratedContent(
                content_type=request.content_type,
                platform=request.platform or "facebook",
                title=ai_result.get("headline", ""),
                caption=ai_result.get("primary_text", ""),
                body=ai_result.get("description", ""),
                prompt_used=request.topic,
                ai_model=ai_content_generator.text_model,
                created_by=None
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported content type: {request.content_type}"
            )

        db.add(new_content)
        db.commit()
        db.refresh(new_content)

        return new_content

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating content: {str(e)}"
        )


@router.get("/", response_model=List[ContentResponse])
async def get_content(
    skip: int = 0,
    limit: int = 50,
    content_type: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all generated content with filters"""

    query = db.query(GeneratedContent)

    if content_type:
        query = query.filter(GeneratedContent.content_type == content_type)

    if platform:
        query = query.filter(GeneratedContent.platform == platform)

    if status:
        query = query.filter(GeneratedContent.status == status)

    content = query.order_by(GeneratedContent.created_at.desc()).offset(skip).limit(limit).all()
    return content


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_by_id(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Get specific content by ID"""

    content = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    return content


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: int,
    update_data: ContentUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update generated content"""

    content = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(content, field, value)

    # If status changed to approved, set approval data
    if update_dict.get("status") == "approved":
        content.approved_by = None
        content.approved_at = datetime.utcnow()

    # If status changed to posted, set posted_at
    if update_dict.get("status") == "posted":
        content.posted_at = datetime.utcnow()

    db.commit()
    db.refresh(content)

    return content


@router.post("/{content_id}/performance")
async def update_content_performance(
    content_id: int,
    performance_data: ContentPerformanceUpdate,
    db: Session = Depends(get_db)
):
    """Update performance metrics for posted content"""

    content = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Update performance metrics
    content.platform_post_id = performance_data.platform_post_id
    content.likes_count = performance_data.likes_count
    content.comments_count = performance_data.comments_count
    content.shares_count = performance_data.shares_count
    content.reach = performance_data.reach

    # Calculate engagement rate
    if content.reach > 0:
        total_engagement = (
            performance_data.likes_count +
            performance_data.comments_count +
            performance_data.shares_count
        )
        content.engagement_rate = (total_engagement / content.reach) * 100

    db.commit()
    db.refresh(content)

    return {"message": "Performance updated successfully", "content": content}


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db)
):
    """Delete generated content"""

    content = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    db.delete(content)
    db.commit()

    return None


@router.post("/improve/{content_id}", response_model=ContentResponse)
async def improve_content(
    content_id: int,
    improvement_focus: str = "engagement",
    db: Session = Depends(get_db)
):
    """Improve existing content using AI"""

    content = db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    try:
        # Get the text to improve
        original_text = content.caption or content.body or ""

        if not original_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No content to improve"
            )

        # Improve the content
        improved_text = await ai_content_generator.improve_content(
            original_content=original_text,
            content_type=content.content_type,
            improvement_focus=improvement_focus
        )

        # Update the content
        if content.caption:
            content.caption = improved_text
        else:
            content.body = improved_text

        content.status = "draft"  # Reset to draft after improvement

        db.commit()
        db.refresh(content)

        return content

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error improving content: {str(e)}"
        )


@router.get("/download-image/{filename}")
async def download_image(filename: str):
    """Download generated image with proper Content-Disposition header"""

    # Construct file path
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Return file with download headers
    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
