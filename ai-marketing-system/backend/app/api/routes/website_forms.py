"""
Website Forms API Routes
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import json
import hashlib

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.website_form import WebsiteForm, FormSubmission
from app.schemas.website_form import (
    WebsiteFormCreate,
    WebsiteFormUpdate,
    WebsiteFormResponse,
    FormSubmissionCreate,
    FormSubmissionResponse,
    FormStats
)

router = APIRouter()


def generate_embed_code(form_id: int, api_url: str = "http://localhost:8000") -> str:
    """Generate embeddable JavaScript code for the form"""
    embed_script = f"""
<!-- AI Marketing System Lead Form -->
<div id="ams-form-{form_id}"></div>
<script>
(function() {{
    var script = document.createElement('script');
    script.src = '{api_url}/api/forms/embed/{form_id}.js';
    script.async = true;
    document.getElementById('ams-form-{form_id}').appendChild(script);
}})();
</script>
<!-- End AI Marketing System Lead Form -->
"""
    return embed_script.strip()


@router.get("/", response_model=List[WebsiteFormResponse])
async def get_forms(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all website forms for the current user"""
    query = db.query(WebsiteForm).filter(WebsiteForm.user_id == current_user.id)

    if is_active is not None:
        query = query.filter(WebsiteForm.is_active == is_active)

    forms = query.order_by(desc(WebsiteForm.created_at)).offset(skip).limit(limit).all()
    return forms


@router.get("/{form_id}", response_model=WebsiteFormResponse)
async def get_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific website form"""
    form = db.query(WebsiteForm).filter(
        WebsiteForm.id == form_id,
        WebsiteForm.user_id == current_user.id
    ).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return form


@router.post("/", response_model=WebsiteFormResponse)
async def create_form(
    form_data: WebsiteFormCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new website form"""
    # Convert fields to JSON
    fields_json = [field.dict() for field in form_data.fields]

    # Create form
    db_form = WebsiteForm(
        user_id=current_user.id,
        name=form_data.name,
        description=form_data.description,
        fields=fields_json,
        submit_text=form_data.submit_text,
        success_message=form_data.success_message
    )

    db.add(db_form)
    db.commit()
    db.refresh(db_form)

    # Generate embed code
    db_form.embed_code = generate_embed_code(db_form.id)
    db.commit()
    db.refresh(db_form)

    return db_form


@router.put("/{form_id}", response_model=WebsiteFormResponse)
async def update_form(
    form_id: int,
    form_update: WebsiteFormUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a website form"""
    form = db.query(WebsiteForm).filter(
        WebsiteForm.id == form_id,
        WebsiteForm.user_id == current_user.id
    ).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # Update fields
    update_data = form_update.dict(exclude_unset=True)

    if "fields" in update_data:
        update_data["fields"] = [field.dict() for field in form_update.fields]

    for field, value in update_data.items():
        setattr(form, field, value)

    form.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(form)

    return form


@router.delete("/{form_id}")
async def delete_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a website form"""
    form = db.query(WebsiteForm).filter(
        WebsiteForm.id == form_id,
        WebsiteForm.user_id == current_user.id
    ).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    db.delete(form)
    db.commit()

    return {"message": "Form deleted successfully"}


@router.post("/{form_id}/submissions", response_model=FormSubmissionResponse)
async def submit_form(
    form_id: int,
    submission: FormSubmissionCreate,
    db: Session = Depends(get_db)
):
    """Submit a form (public endpoint for embedded forms)"""
    form = db.query(WebsiteForm).filter(
        WebsiteForm.id == form_id,
        WebsiteForm.is_active == True
    ).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found or inactive"
        )

    # Create submission
    db_submission = FormSubmission(
        form_id=form_id,
        data=submission.data,
        source_url=submission.source_url
    )

    db.add(db_submission)

    # Update form submission count
    form.submission_count += 1

    # Calculate conversion rate (mock calculation for now)
    if form.submission_count > 0:
        form.conversion_rate = min(100, form.submission_count * 2.5)  # Mock conversion rate

    db.commit()
    db.refresh(db_submission)

    return db_submission


@router.get("/{form_id}/submissions", response_model=List[FormSubmissionResponse])
async def get_form_submissions(
    form_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all submissions for a form"""
    # Verify form ownership
    form = db.query(WebsiteForm).filter(
        WebsiteForm.id == form_id,
        WebsiteForm.user_id == current_user.id
    ).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    submissions = db.query(FormSubmission).filter(
        FormSubmission.form_id == form_id
    ).order_by(desc(FormSubmission.created_at)).offset(skip).limit(limit).all()

    return submissions


@router.get("/{form_id}/stats", response_model=FormStats)
async def get_form_stats(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a form"""
    # Verify form ownership
    form = db.query(WebsiteForm).filter(
        WebsiteForm.id == form_id,
        WebsiteForm.user_id == current_user.id
    ).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    # Calculate time-based stats
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    submissions_today = db.query(func.count(FormSubmission.id)).filter(
        FormSubmission.form_id == form_id,
        FormSubmission.created_at >= today
    ).scalar()

    submissions_week = db.query(func.count(FormSubmission.id)).filter(
        FormSubmission.form_id == form_id,
        FormSubmission.created_at >= week_ago
    ).scalar()

    submissions_month = db.query(func.count(FormSubmission.id)).filter(
        FormSubmission.form_id == form_id,
        FormSubmission.created_at >= month_ago
    ).scalar()

    # Get top sources
    top_sources = db.query(
        FormSubmission.source_url,
        func.count(FormSubmission.id).label('count')
    ).filter(
        FormSubmission.form_id == form_id,
        FormSubmission.source_url.isnot(None)
    ).group_by(FormSubmission.source_url).order_by(
        desc('count')
    ).limit(5).all()

    return FormStats(
        form_id=form_id,
        form_name=form.name,
        total_submissions=form.submission_count,
        conversion_rate=form.conversion_rate,
        submissions_today=submissions_today or 0,
        submissions_week=submissions_week or 0,
        submissions_month=submissions_month or 0,
        top_sources=[{"url": url, "count": count} for url, count in top_sources]
    )


@router.get("/embed/{form_id}.js")
async def get_embed_script(
    form_id: int,
    db: Session = Depends(get_db)
):
    """Get the JavaScript embed code for a form (public endpoint)"""
    form = db.query(WebsiteForm).filter(
        WebsiteForm.id == form_id,
        WebsiteForm.is_active == True
    ).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found or inactive"
        )

    # Generate JavaScript that creates the form
    js_code = f"""
(function() {{
    var formContainer = document.getElementById('ams-form-{form_id}');
    if (!formContainer) return;

    var formHTML = '<form id="ams-embed-form-{form_id}" style="max-width: 500px; margin: 0 auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">';
    formHTML += '<h3 style="margin-bottom: 20px;">{form.name}</h3>';
    """

    # Add form fields
    for field in form.fields:
        field_id = f"ams-field-{form_id}-{field['id']}"
        required = "required" if field.get('required') else ""

        js_code += f"""
    formHTML += '<div style="margin-bottom: 15px;">';
    formHTML += '<label for="{field_id}" style="display: block; margin-bottom: 5px; font-weight: 500;">{field['label']}</label>';
    """

        if field['type'] in ['text', 'email', 'tel']:
            placeholder = field.get('placeholder', '')
            js_code += f"""
    formHTML += '<input type="{field['type']}" id="{field_id}" name="{field['id']}" placeholder="{placeholder}" {required} style="width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px;" />';
    """
        elif field['type'] == 'textarea':
            placeholder = field.get('placeholder', '')
            js_code += f"""
    formHTML += '<textarea id="{field_id}" name="{field['id']}" placeholder="{placeholder}" {required} style="width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; min-height: 100px;"></textarea>';
    """

        js_code += """
    formHTML += '</div>';
    """

    # Add submit button
    js_code += f"""
    formHTML += '<button type="submit" style="width: 100%; padding: 10px 20px; background: #4F46E5; color: white; border: none; border-radius: 4px; font-weight: 500; cursor: pointer;">{form.submit_text}</button>';
    formHTML += '</form>';

    formContainer.innerHTML = formHTML;

    // Handle form submission
    document.getElementById('ams-embed-form-{form_id}').addEventListener('submit', function(e) {{
        e.preventDefault();
        var formData = new FormData(e.target);
        var data = {{}};
        formData.forEach(function(value, key) {{
            data[key] = value;
        }});

        fetch('http://localhost:8000/api/forms/{form_id}/submissions', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
            }},
            body: JSON.stringify({{
                form_id: {form_id},
                data: data,
                source_url: window.location.href
            }})
        }})
        .then(response => response.json())
        .then(data => {{
            formContainer.innerHTML = '<div style="padding: 20px; background: #10B981; color: white; border-radius: 8px; text-align: center;">{form.success_message}</div>';
        }})
        .catch(error => {{
            console.error('Error:', error);
            alert('There was an error submitting the form. Please try again.');
        }});
    }});
}})();
"""

    return js_code