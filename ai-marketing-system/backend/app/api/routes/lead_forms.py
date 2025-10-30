"""
Lead Forms API Routes

Endpoints for creating and managing website lead capture forms.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import re

from app.db.session import get_db
from app.models.lead_form import LeadForm, LeadFormSubmission
from app.models.lead import Lead, LeadSource
from app.models.user import User
from app.core.security import get_current_active_user
from app.schemas.lead_form import (
    FormCreate,
    FormUpdate,
    FormResponse,
    FormSubmissionData,
    FormSubmissionResponse,
    FormStatsResponse
)

router = APIRouter()


@router.post("/", response_model=FormResponse, status_code=status.HTTP_201_CREATED)
async def create_form(
    form_data: FormCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new lead capture form"""

    # Check if slug already exists
    existing = db.query(LeadForm).filter(LeadForm.slug == form_data.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Form with slug '{form_data.slug}' already exists"
        )

    # Convert fields to JSON-serializable format
    fields_json = [field.dict() for field in form_data.fields]

    new_form = LeadForm(
        **form_data.dict(exclude={"fields"}),
        fields=fields_json,
        user_id=current_user.id if current_user else None
    )

    db.add(new_form)
    db.commit()
    db.refresh(new_form)

    return new_form


@router.get("/", response_model=List[FormResponse])
async def get_forms(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all forms"""

    query = db.query(LeadForm)

    if current_user:
        query = query.filter(LeadForm.user_id == current_user.id)

    if is_active is not None:
        query = query.filter(LeadForm.is_active == is_active)

    forms = query.order_by(LeadForm.created_at.desc()).offset(skip).limit(limit).all()
    return forms


@router.get("/{form_id}", response_model=FormResponse)
async def get_form(
    form_id: int,
    db: Session = Depends(get_db)
):
    """Get form by ID"""

    form = db.query(LeadForm).filter(LeadForm.id == form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return form


@router.get("/slug/{slug}", response_model=FormResponse)
async def get_form_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get form by slug (for public embedding)"""

    form = db.query(LeadForm).filter(LeadForm.slug == slug).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    if not form.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This form is no longer active"
        )

    return form


@router.put("/{form_id}", response_model=FormResponse)
async def update_form(
    form_id: int,
    form_data: FormUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a form"""

    form = db.query(LeadForm).filter(LeadForm.id == form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # Update fields
    update_dict = form_data.dict(exclude_unset=True)

    # Handle fields separately
    if "fields" in update_dict and update_dict["fields"]:
        update_dict["fields"] = [field.dict() for field in update_dict["fields"]]

    for field, value in update_dict.items():
        setattr(form, field, value)

    form.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(form)

    return form


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a form"""

    form = db.query(LeadForm).filter(LeadForm.id == form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    db.delete(form)
    db.commit()

    return None


@router.post("/{form_id}/duplicate", response_model=FormResponse)
async def duplicate_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Duplicate an existing form"""

    original = db.query(LeadForm).filter(LeadForm.id == form_id).first()
    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # Create new slug
    new_slug = f"{original.slug}-copy"
    counter = 1
    while db.query(LeadForm).filter(LeadForm.slug == new_slug).first():
        new_slug = f"{original.slug}-copy-{counter}"
        counter += 1

    # Create duplicate
    duplicate = LeadForm(
        name=f"{original.name} (Copy)",
        slug=new_slug,
        title=original.title,
        description=original.description,
        submit_button_text=original.submit_button_text,
        success_message=original.success_message,
        fields=original.fields,
        theme_color=original.theme_color,
        background_color=original.background_color,
        text_color=original.text_color,
        redirect_url=original.redirect_url,
        enable_double_optin=original.enable_double_optin,
        require_consent=original.require_consent,
        consent_text=original.consent_text,
        enable_recaptcha=original.enable_recaptcha,
        enable_honeypot=original.enable_honeypot,
        rate_limit_enabled=original.rate_limit_enabled,
        max_submissions_per_ip=original.max_submissions_per_ip,
        user_id=current_user.id if current_user else None
    )

    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)

    return duplicate


# PUBLIC ENDPOINT - No authentication required
@router.post("/submit/{slug}", response_model=FormSubmissionResponse)
async def submit_form(
    slug: str,
    submission: FormSubmissionData,
    request: Request,
    db: Session = Depends(get_db)
):
    """Public endpoint for form submissions"""

    # Get form
    form = db.query(LeadForm).filter(LeadForm.slug == slug, LeadForm.is_active == True).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found or inactive"
        )

    # Honeypot spam protection
    if form.enable_honeypot and submission.honeypot:
        # Bot detected - silently reject
        return FormSubmissionResponse(
            success=True,
            message=form.success_message,
            redirect_url=form.redirect_url
        )

    # Rate limiting
    if form.rate_limit_enabled:
        client_ip = request.client.host
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        recent_submissions = db.query(LeadFormSubmission).filter(
            LeadFormSubmission.form_id == form.id,
            LeadFormSubmission.ip_address == client_ip,
            LeadFormSubmission.submitted_at >= one_hour_ago
        ).count()

        if recent_submissions >= form.max_submissions_per_ip:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many submissions. Please try again later."
            )

    # Validate required fields
    data = submission.data
    for field in form.fields:
        if field.get("required") and not data.get(field["name"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field['label']}' is required"
            )

    # Email validation
    email = data.get("email")
    if email and not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address"
        )

    # Create submission record
    submission_record = LeadFormSubmission(
        form_id=form.id,
        data=data,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer")
    )

    db.add(submission_record)

    # Create lead if email provided
    lead_id = None
    if email:
        # Check for duplicate
        existing_lead = db.query(Lead).filter(Lead.email == email).first()

        if not existing_lead:
            # Extract consent from checkbox
            consent = data.get("consent", False) if form.require_consent else True

            new_lead = Lead(
                email=email,
                first_name=data.get("first_name", data.get("name", "")),
                last_name=data.get("last_name", ""),
                phone=data.get("phone", ""),
                source=LeadSource.WEBSITE,
                email_consent=consent,
                consent_date=datetime.utcnow() if consent else None,
                consent_source=f"website_form_{slug}",
                notes=f"Submitted via form: {form.name}"
            )

            db.add(new_lead)
            db.flush()  # Get the ID
            lead_id = new_lead.id

            submission_record.lead_id = lead_id
            submission_record.status = "processed"
            submission_record.processed_at = datetime.utcnow()
        else:
            lead_id = existing_lead.id
            submission_record.lead_id = lead_id
            submission_record.status = "processed"
            submission_record.processed_at = datetime.utcnow()

    # Update form submission count
    form.submission_count += 1

    db.commit()

    return FormSubmissionResponse(
        success=True,
        message=form.success_message,
        lead_id=lead_id,
        redirect_url=form.redirect_url
    )


@router.get("/{form_id}/stats", response_model=FormStatsResponse)
async def get_form_stats(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get form statistics"""

    form = db.query(LeadForm).filter(LeadForm.id == form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    total = db.query(LeadFormSubmission).filter(LeadFormSubmission.form_id == form_id).count()
    pending = db.query(LeadFormSubmission).filter(
        LeadFormSubmission.form_id == form_id,
        LeadFormSubmission.status == "pending"
    ).count()
    processed = db.query(LeadFormSubmission).filter(
        LeadFormSubmission.form_id == form_id,
        LeadFormSubmission.status == "processed"
    ).count()
    spam = db.query(LeadFormSubmission).filter(
        LeadFormSubmission.form_id == form_id,
        LeadFormSubmission.status == "spam"
    ).count()

    conversion_rate = (processed / total * 100) if total > 0 else 0

    # Get recent submissions
    recent = db.query(LeadFormSubmission).filter(
        LeadFormSubmission.form_id == form_id
    ).order_by(LeadFormSubmission.submitted_at.desc()).limit(10).all()

    recent_submissions = [
        {
            "id": sub.id,
            "data": sub.data,
            "status": sub.status,
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None
        }
        for sub in recent
    ]

    return FormStatsResponse(
        total_submissions=total,
        pending_submissions=pending,
        processed_submissions=processed,
        spam_submissions=spam,
        conversion_rate=round(conversion_rate, 2),
        recent_submissions=recent_submissions
    )
