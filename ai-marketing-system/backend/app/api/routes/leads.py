from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
import pandas as pd
import io

from app.db.session import get_db
from app.models.lead import Lead
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadImportRequest
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db)
):
    """Create a new lead with consent tracking"""

    # Check if lead already exists
    existing_lead = db.query(Lead).filter(Lead.email == lead_data.email).first()
    if existing_lead:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead with this email already exists"
        )

    # Create new lead
    new_lead = Lead(
        **lead_data.dict(),
        consent_date=datetime.utcnow() if lead_data.email_consent or lead_data.sms_consent else None
    )

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return new_lead


@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    sport_type: Optional[str] = None,
    email_consent: Optional[bool] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all leads with optional filters"""

    query = db.query(Lead)

    # Apply filters
    if status:
        query = query.filter(Lead.status == status)

    if sport_type:
        query = query.filter(Lead.sport_type == sport_type)

    if email_consent is not None:
        query = query.filter(Lead.email_consent == email_consent)

    if source:
        query = query.filter(Lead.source == source)

    if search:
        query = query.filter(
            or_(
                Lead.email.ilike(f"%{search}%"),
                Lead.first_name.ilike(f"%{search}%"),
                Lead.last_name.ilike(f"%{search}%")
            )
        )

    leads = query.offset(skip).limit(limit).all()
    return leads


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific lead by ID"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db)
):
    """Update a lead"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Update fields
    update_data = lead_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    # Update consent date if consent status changed
    if "email_consent" in update_data or "sms_consent" in update_data:
        if lead.email_consent or lead.sms_consent:
            lead.consent_date = datetime.utcnow()

    db.commit()
    db.refresh(lead)

    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Delete a lead"""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    db.delete(lead)
    db.commit()

    return None


@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_leads(
    file: UploadFile = File(...),
    consent_confirmed: bool = False,
    source: str = "import",
    db: Session = Depends(get_db)
):
    """Import leads from CSV or Excel file"""

    if not consent_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must confirm that all imported contacts have given consent"
        )

    # Read file
    contents = await file.read()

    try:
        # Try to read as CSV or Excel
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be CSV or Excel format"
            )

        # Validate required columns
        required_columns = ['email']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must contain columns: {', '.join(required_columns)}"
            )

        # Import leads
        imported = 0
        skipped = 0
        errors = []

        for _, row in df.iterrows():
            try:
                # Check if lead already exists
                existing = db.query(Lead).filter(Lead.email == row['email']).first()
                if existing:
                    skipped += 1
                    continue

                # Create new lead
                new_lead = Lead(
                    email=row['email'],
                    first_name=row.get('first_name', ''),
                    last_name=row.get('last_name', ''),
                    phone=row.get('phone', ''),
                    location=row.get('location', ''),
                    sport_type=row.get('sport_type', ''),
                    customer_type=row.get('customer_type', ''),
                    email_consent=True,
                    consent_date=datetime.utcnow(),
                    consent_source=source,
                    source=source
                )

                db.add(new_lead)
                imported += 1

            except Exception as e:
                errors.append(f"Row {_ + 1}: {str(e)}")

        db.commit()

        return {
            "message": "Import completed",
            "imported": imported,
            "skipped": skipped,
            "errors": errors
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing file: {str(e)}"
        )


@router.get("/stats/overview")
async def get_leads_stats(
    db: Session = Depends(get_db)
):
    """Get leads statistics"""

    total_leads = db.query(Lead).count()
    opted_in = db.query(Lead).filter(Lead.email_consent == True).count()
    new_leads = db.query(Lead).filter(Lead.status == "new").count()
    customers = db.query(Lead).filter(Lead.status == "customer").count()

    # Get breakdown by source
    from sqlalchemy import func
    source_breakdown = db.query(
        Lead.source,
        func.count(Lead.id).label('count')
    ).group_by(Lead.source).all()

    by_source = {source: count for source, count in source_breakdown}

    return {
        "total_leads": total_leads,
        "opted_in": opted_in,
        "new_leads": new_leads,
        "customers": customers,
        "opt_in_rate": (opted_in / total_leads * 100) if total_leads > 0 else 0,
        "by_source": by_source
    }


@router.get("/stats/by-source")
async def get_leads_stats_by_source(
    db: Session = Depends(get_db)
):
    """Get detailed lead statistics broken down by source"""

    from sqlalchemy import func
    from app.models.lead import LeadSource

    # Get all sources
    source_stats = []

    for source in LeadSource:
        source_leads = db.query(Lead).filter(Lead.source == source.value)

        total = source_leads.count()
        if total == 0:
            continue  # Skip sources with no leads

        opted_in = source_leads.filter(Lead.email_consent == True).count()
        new = source_leads.filter(Lead.status == "new").count()
        customers = source_leads.filter(Lead.status == "customer").count()

        source_stats.append({
            "source": source.value,
            "total_leads": total,
            "opted_in": opted_in,
            "new_leads": new,
            "customers": customers,
            "opt_in_rate": round((opted_in / total * 100), 2) if total > 0 else 0,
            "customer_conversion_rate": round((customers / total * 100), 2) if total > 0 else 0
        })

    # Sort by total leads descending
    source_stats.sort(key=lambda x: x["total_leads"], reverse=True)

    return {
        "sources": source_stats,
        "total_sources": len(source_stats)
    }
