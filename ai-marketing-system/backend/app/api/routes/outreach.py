from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.outreach import OutreachMessage, OutreachSequence, OutreachEnrollment
from app.models.lead import Lead
from app.models.user import User
from app.schemas.outreach import (
    OutreachMessageCreate, OutreachMessageUpdate, OutreachMessageResponse,
    OutreachSequenceCreate, OutreachSequenceUpdate, OutreachSequenceResponse,
    EnrollmentCreate, EnrollmentResponse, SequenceAnalytics,
    PersonalizedMessageRequest, PersonalizedMessageResponse
)
from app.core.security import get_current_active_user
from app.services.outreach_service import outreach_service

router = APIRouter()


# ============= Outreach Messages =============

@router.post("/messages", response_model=OutreachMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_outreach_message(
    message_data: OutreachMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new outreach message"""

    # Verify lead exists and belongs to user
    lead = db.query(Lead).filter(Lead.id == message_data.lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    new_message = OutreachMessage(
        **message_data.dict(),
        user_id=current_user.id,
        status="draft"
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


@router.get("/messages", response_model=List[OutreachMessageResponse])
async def get_outreach_messages(
    skip: int = 0,
    limit: int = 50,
    lead_id: Optional[int] = None,
    sequence_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all outreach messages with filters"""

    query = db.query(OutreachMessage).filter(OutreachMessage.user_id == current_user.id)

    if lead_id:
        query = query.filter(OutreachMessage.lead_id == lead_id)

    if sequence_id:
        query = query.filter(OutreachMessage.sequence_id == sequence_id)

    if status:
        query = query.filter(OutreachMessage.status == status)

    messages = query.order_by(OutreachMessage.created_at.desc()).offset(skip).limit(limit).all()
    return messages


@router.get("/messages/{message_id}", response_model=OutreachMessageResponse)
async def get_outreach_message(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific outreach message by ID"""

    message = db.query(OutreachMessage).filter(
        OutreachMessage.id == message_id,
        OutreachMessage.user_id == current_user.id
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    return message


@router.post("/messages/{message_id}/send", response_model=OutreachMessageResponse)
async def send_outreach_message(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send an outreach message immediately"""

    message = db.query(OutreachMessage).filter(
        OutreachMessage.id == message_id,
        OutreachMessage.user_id == current_user.id
    ).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    lead = db.query(Lead).filter(Lead.id == message.lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    # Send the message
    success = await outreach_service.send_outreach_message(message, lead, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {message.error_message}"
        )

    db.refresh(message)
    return message


# ============= Personalized Message Generation =============

@router.post("/generate-message", response_model=PersonalizedMessageResponse)
async def generate_personalized_message(
    request: PersonalizedMessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized outreach message for a lead using AI"""

    lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    try:
        message_data = await outreach_service.generate_personalized_message(
            lead=lead,
            message_type=request.message_type,
            template=request.template,
            additional_context=request.additional_context
        )

        return PersonalizedMessageResponse(**message_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate message: {str(e)}"
        )


# ============= Outreach Sequences =============

@router.post("/sequences", response_model=OutreachSequenceResponse, status_code=status.HTTP_201_CREATED)
async def create_outreach_sequence(
    sequence_data: OutreachSequenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new outreach sequence"""

    try:
        sequence = await outreach_service.create_sequence(
            name=sequence_data.name,
            description=sequence_data.description,
            steps=sequence_data.sequence_steps,
            user_id=current_user.id,
            segment_id=sequence_data.segment_id,
            target_filters=sequence_data.target_filters,
            db=db
        )

        return sequence

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sequence: {str(e)}"
        )


@router.get("/sequences", response_model=List[OutreachSequenceResponse])
async def get_outreach_sequences(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all outreach sequences"""

    query = db.query(OutreachSequence).filter(OutreachSequence.user_id == current_user.id)

    if status:
        query = query.filter(OutreachSequence.status == status)

    sequences = query.order_by(OutreachSequence.created_at.desc()).offset(skip).limit(limit).all()
    return sequences


@router.get("/sequences/{sequence_id}", response_model=OutreachSequenceResponse)
async def get_outreach_sequence(
    sequence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific outreach sequence by ID"""

    sequence = db.query(OutreachSequence).filter(
        OutreachSequence.id == sequence_id,
        OutreachSequence.user_id == current_user.id
    ).first()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found"
        )

    return sequence


@router.put("/sequences/{sequence_id}", response_model=OutreachSequenceResponse)
async def update_outreach_sequence(
    sequence_id: int,
    sequence_data: OutreachSequenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an outreach sequence"""

    sequence = db.query(OutreachSequence).filter(
        OutreachSequence.id == sequence_id,
        OutreachSequence.user_id == current_user.id
    ).first()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found"
        )

    # Don't allow updating active sequences
    if sequence.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update active sequences. Pause the sequence first."
        )

    # Update fields
    update_data = sequence_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sequence, field, value)

    db.commit()
    db.refresh(sequence)

    return sequence


@router.delete("/sequences/{sequence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outreach_sequence(
    sequence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an outreach sequence"""

    sequence = db.query(OutreachSequence).filter(
        OutreachSequence.id == sequence_id,
        OutreachSequence.user_id == current_user.id
    ).first()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found"
        )

    if sequence.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active sequences. Pause the sequence first."
        )

    db.delete(sequence)
    db.commit()


# ============= Sequence Enrollments =============

@router.post("/sequences/{sequence_id}/enroll")
async def enroll_leads_in_sequence(
    sequence_id: int,
    enrollment_data: EnrollmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enroll leads into a sequence"""

    sequence = db.query(OutreachSequence).filter(
        OutreachSequence.id == sequence_id,
        OutreachSequence.user_id == current_user.id
    ).first()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found"
        )

    try:
        results = await outreach_service.enroll_leads_in_sequence(
            sequence_id=sequence_id,
            lead_ids=enrollment_data.lead_ids,
            db=db
        )

        # Update sequence status to active if it was draft
        if sequence.status == "draft":
            sequence.status = "active"
            sequence.started_at = datetime.utcnow()
            db.commit()

        return {
            "message": "Enrollment complete",
            "results": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enroll leads: {str(e)}"
        )


@router.get("/sequences/{sequence_id}/enrollments", response_model=List[EnrollmentResponse])
async def get_sequence_enrollments(
    sequence_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all enrollments for a sequence"""

    sequence = db.query(OutreachSequence).filter(
        OutreachSequence.id == sequence_id,
        OutreachSequence.user_id == current_user.id
    ).first()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found"
        )

    query = db.query(OutreachEnrollment).filter(
        OutreachEnrollment.sequence_id == sequence_id
    )

    if status:
        query = query.filter(OutreachEnrollment.status == status)

    enrollments = query.order_by(OutreachEnrollment.enrolled_at.desc()).offset(skip).limit(limit).all()
    return enrollments


@router.post("/sequences/{sequence_id}/enrollments/{lead_id}/stop")
async def stop_sequence_for_lead(
    sequence_id: int,
    lead_id: int,
    reason: str = "manual",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Stop a sequence for a specific lead"""

    sequence = db.query(OutreachSequence).filter(
        OutreachSequence.id == sequence_id,
        OutreachSequence.user_id == current_user.id
    ).first()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found"
        )

    success = await outreach_service.stop_sequence_for_lead(
        sequence_id=sequence_id,
        lead_id=lead_id,
        reason=reason,
        db=db
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )

    return {"message": "Sequence stopped for lead"}


# ============= Analytics =============

@router.get("/sequences/{sequence_id}/analytics", response_model=SequenceAnalytics)
async def get_sequence_analytics(
    sequence_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a sequence"""

    sequence = db.query(OutreachSequence).filter(
        OutreachSequence.id == sequence_id,
        OutreachSequence.user_id == current_user.id
    ).first()

    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sequence not found"
        )

    try:
        analytics = outreach_service.get_sequence_analytics(sequence_id, db)
        return SequenceAnalytics(**analytics)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics: {str(e)}"
        )


# ============= Background Processing =============

@router.post("/process-sequences", status_code=status.HTTP_202_ACCEPTED)
async def process_pending_sequences(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process all pending sequence steps (called by scheduler)"""

    # Add background task to process sequences
    background_tasks.add_task(outreach_service.process_pending_sequences, db)

    return {"message": "Sequence processing started"}
