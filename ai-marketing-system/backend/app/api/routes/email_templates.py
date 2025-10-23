from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.email_template import EmailTemplate
from app.schemas.email_template import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse,
    TemplateRenderRequest,
    TemplateRenderResponse
)
from app.services.template_service import template_service

router = APIRouter()


@router.post("/", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: EmailTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new email template"""
    
    # Validate template syntax
    validation = template_service.validate_template(template_data.html_content)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template validation failed: {', '.join(validation['errors'])}"
        )
    
    # If setting as default, unset other defaults in same category
    if template_data.is_default:
        db.query(EmailTemplate).filter(
            EmailTemplate.category == template_data.category,
            EmailTemplate.is_default == True
        ).update({"is_default": False})
    
    # Create new template
    new_template = EmailTemplate(
        **template_data.model_dump(),
        created_by=None
    )
    
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return new_template


@router.get("/", response_model=List[EmailTemplateResponse])
async def get_templates(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all email templates with optional filters"""
    
    query = db.query(EmailTemplate)
    
    # Apply filters
    if category:
        query = query.filter(EmailTemplate.category == category)
    
    if is_active is not None:
        query = query.filter(EmailTemplate.is_active == is_active)
    
    if search:
        query = query.filter(
            (EmailTemplate.name.ilike(f"%{search}%")) |
            (EmailTemplate.description.ilike(f"%{search}%"))
        )
    
    templates = query.order_by(EmailTemplate.created_at.desc()).offset(skip).limit(limit).all()
    return templates


@router.get("/{template_id}", response_model=EmailTemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific email template by ID"""
    
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template


@router.put("/{template_id}", response_model=EmailTemplateResponse)
async def update_template(
    template_id: int,
    template_data: EmailTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update an email template"""
    
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Validate template if HTML content is being updated
    update_dict = template_data.model_dump(exclude_unset=True)
    if "html_content" in update_dict:
        validation = template_service.validate_template(update_dict["html_content"])
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template validation failed: {', '.join(validation['errors'])}"
            )
    
    # If setting as default, unset other defaults in same category
    if update_dict.get("is_default") and template.category:
        db.query(EmailTemplate).filter(
            EmailTemplate.category == template.category,
            EmailTemplate.is_default == True,
            EmailTemplate.id != template_id
        ).update({"is_default": False})
    
    # Update fields
    for field, value in update_dict.items():
        setattr(template, field, value)
    
    template.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(template)
    
    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Delete an email template"""
    
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    db.delete(template)
    db.commit()
    
    return None


@router.post("/render", response_model=TemplateRenderResponse)
async def render_template(
    request: TemplateRenderRequest,
    db: Session = Depends(get_db)
):
    """Render a template with provided variables for preview"""
    
    template = db.query(EmailTemplate).filter(EmailTemplate.id == request.template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Prepare variables with defaults
    variables = template_service.prepare_variables(request.variables)
    
    # Render template
    rendered_subject = template_service.render_template(template.subject, variables)
    rendered_html = template_service.render_template(template.html_content, variables)
    rendered_plain = None
    if template.plain_text_content:
        rendered_plain = template_service.render_template(template.plain_text_content, variables)
    
    return TemplateRenderResponse(
        subject=rendered_subject,
        html_content=rendered_html,
        plain_text_content=rendered_plain
    )


@router.post("/{template_id}/duplicate", response_model=EmailTemplateResponse)
async def duplicate_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Duplicate an existing template"""
    
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Create a copy
    new_template = EmailTemplate(
        name=f"{template.name} (Copy)",
        description=template.description,
        category=template.category,
        subject=template.subject,
        html_content=template.html_content,
        plain_text_content=template.plain_text_content,
        available_variables=template.available_variables,
        is_active=True,
        is_default=False,  # Copies are never default
        created_by=None
    )
    
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    return new_template


@router.get("/{template_id}/validate")
async def validate_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Validate a template's syntax and structure"""
    
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    validation = template_service.validate_template(template.html_content)
    
    return {
        "template_id": template_id,
        "template_name": template.name,
        **validation
    }


@router.get("/categories/list")
async def get_categories():
    """Get list of available template categories"""
    
    return {
        "categories": [
            {"value": "welcome", "label": "Welcome"},
            {"value": "promotional", "label": "Promotional"},
            {"value": "newsletter", "label": "Newsletter"},
            {"value": "transactional", "label": "Transactional"},
            {"value": "general", "label": "General"},
        ]
    }


@router.get("/variables/list")
async def get_available_variables():
    """Get list of available template variables"""
    
    return {
        "variables": template_service.get_default_variables(),
        "examples": {
            "simple": "{{first_name}}",
            "with_default": "{{first_name|default:\"Valued Customer\"}}",
            "with_filter": "{{first_name|capitalize}}",
        }
    }

