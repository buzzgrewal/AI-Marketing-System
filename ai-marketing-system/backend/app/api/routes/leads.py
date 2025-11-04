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


# ============= Lead Enrichment & Deduplication =============

@router.get("/{lead_id}/duplicates")
async def find_lead_duplicates(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Find duplicate leads for a specific lead"""
    from app.services.lead_enrichment_service import lead_enrichment_service

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    duplicates = lead_enrichment_service.find_duplicates(db, lead_id=lead_id)

    return {
        "lead_id": lead_id,
        "duplicates_found": len(duplicates),
        "duplicates": [
            {
                "id": dup.id,
                "email": dup.email,
                "first_name": dup.first_name,
                "last_name": dup.last_name,
                "phone": dup.phone,
                "created_at": dup.created_at.isoformat() if dup.created_at else None
            }
            for dup in duplicates
        ]
    }


@router.post("/{lead_id}/merge")
async def merge_leads(
    lead_id: int,
    duplicate_ids: List[int],
    db: Session = Depends(get_db)
):
    """Merge duplicate leads into this lead"""
    from app.services.lead_enrichment_service import lead_enrichment_service

    try:
        merged_lead = lead_enrichment_service.merge_leads(lead_id, duplicate_ids, db)

        return {
            "message": "Leads merged successfully",
            "primary_lead_id": merged_lead.id,
            "merged_count": len(duplicate_ids)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to merge leads: {str(e)}"
        )


@router.post("/deduplicate")
async def auto_deduplicate(
    dry_run: bool = True,
    db: Session = Depends(get_db)
):
    """Automatically find and merge duplicate leads"""
    from app.services.lead_enrichment_service import lead_enrichment_service

    try:
        results = lead_enrichment_service.auto_deduplicate(db, dry_run=dry_run)

        return {
            "message": "Deduplication complete" if not dry_run else "Deduplication analysis complete (dry run)",
            "dry_run": dry_run,
            **results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deduplicate: {str(e)}"
        )


@router.post("/{lead_id}/enrich", response_model=LeadResponse)
async def enrich_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Enrich a lead with derived data"""
    from app.services.lead_enrichment_service import lead_enrichment_service

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        enriched_lead = lead_enrichment_service.enrich_lead(lead, db)
        return enriched_lead

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enrich lead: {str(e)}"
        )


@router.post("/bulk-enrich")
async def bulk_enrich_leads(
    lead_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db)
):
    """Enrich multiple leads at once"""
    from app.services.lead_enrichment_service import lead_enrichment_service

    try:
        results = lead_enrichment_service.bulk_enrich(db, lead_ids=lead_ids)

        return {
            "message": "Bulk enrichment complete",
            **results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk enrich: {str(e)}"
        )


@router.get("/{lead_id}/quality")
async def get_lead_quality_score(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive quality score for a lead"""
    from app.services.lead_enrichment_service import lead_enrichment_service

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        quality_data = lead_enrichment_service.calculate_lead_quality(lead, db)

        return {
            "lead_id": lead_id,
            "email": lead.email,
            "name": f"{lead.first_name or ''} {lead.last_name or ''}".strip(),
            **quality_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate quality score: {str(e)}"
        )


@router.post("/{lead_id}/clean", response_model=LeadResponse)
async def clean_lead_data(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Clean and standardize lead data"""
    from app.services.lead_enrichment_service import lead_enrichment_service

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        cleaned_lead = lead_enrichment_service.clean_lead_data(lead, db)
        return cleaned_lead

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clean lead data: {str(e)}"
        )
