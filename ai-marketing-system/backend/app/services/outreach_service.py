import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.outreach import (
    OutreachMessage, OutreachSequence, OutreachEnrollment,
    OutreachStatus, OutreachType, SequenceStatus
)
from app.models.lead import Lead, LeadStatus
from app.services.ai_content_generator import ai_content_generator
from app.services.email_service import email_service


class OutreachService:
    """Service for generating and managing personalized outreach campaigns"""

    async def generate_personalized_message(
        self,
        lead: Lead,
        message_type: str = "intro",
        template: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate a personalized outreach message for a specific lead using AI"""

        # Build personalization context
        lead_context = {
            "first_name": lead.first_name or "there",
            "location": lead.location or "your area",
            "sport_type": lead.sport_type or "endurance sports",
            "customer_type": lead.customer_type or "athlete",
            "interests": lead.interests or "cycling and triathlon"
        }

        # Message type templates
        message_templates = {
            "intro": {
                "purpose": "introductory outreach to establish connection",
                "tone": "friendly and professional",
                "focus": "value proposition and building rapport"
            },
            "follow_up": {
                "purpose": "following up on previous message",
                "tone": "helpful and persistent",
                "focus": "addressing pain points and offering solutions"
            },
            "promotional": {
                "purpose": "promoting specific products or offers",
                "tone": "enthusiastic and informative",
                "focus": "benefits and limited-time offers"
            },
            "re_engagement": {
                "purpose": "re-engaging inactive leads",
                "tone": "curious and value-focused",
                "focus": "checking in and offering new value"
            }
        }

        template_config = message_templates.get(message_type, message_templates["intro"])

        # Build AI prompt for personalized message
        prompt = f"""Generate a highly personalized outreach email for a potential customer.

Lead Information:
- Name: {lead_context['first_name']}
- Location: {lead_context['location']}
- Sport/Activity: {lead_context['sport_type']}
- Customer Type: {lead_context['customer_type']}
- Interests: {lead_context['interests']}
- Lead Status: {lead.status}

Message Type: {message_type}
Purpose: {template_config['purpose']}
Tone: {template_config['tone']}
Focus: {template_config['focus']}

{f'Template Guidelines: {template}' if template else ''}
{f'Additional Context: {additional_context}' if additional_context else ''}

Company Context:
We are Premier Bike and Position One Sports, specializing in cycling, triathlon, and running products.
We serve athletes, coaches, teams, and bike fitters with premium equipment and expert guidance.

Generate a personalized email that:
1. Uses the lead's name naturally
2. References their specific sport/interest
3. Addresses their needs as a {lead_context['customer_type']}
4. Includes a clear, non-pushy call-to-action
5. Feels personal and authentic, not template-like
6. Is concise (250-350 words)

Return the response ONLY as valid JSON in this exact format (no markdown, no extra text):
{{
    "subject": "compelling subject line that includes personalization",
    "body": "full email body in plain text format with proper paragraphs",
    "preview_text": "engaging preview text (max 90 chars)",
    "call_to_action": "clear CTA text",
    "personalization_tokens": {{"first_name": "{lead_context['first_name']}", "sport_type": "{lead_context['sport_type']}"}}
}}

IMPORTANT: Return ONLY the JSON object, nothing else before or after it.
"""

        result = await ai_content_generator._call_openrouter(
            prompt,
            ai_content_generator.text_model
        )
        return ai_content_generator._parse_json_response(result)

    async def send_outreach_message(
        self,
        message: OutreachMessage,
        lead: Lead,
        db: Session
    ) -> bool:
        """Send an individual outreach message"""

        try:
            # Check lead consent
            if message.outreach_type == OutreachType.EMAIL and not lead.email_consent:
                raise Exception(f"Lead {lead.email} does not have email consent")

            if message.outreach_type == OutreachType.SMS and not lead.sms_consent:
                raise Exception(f"Lead {lead.phone} does not have SMS consent")

            # Send based on outreach type
            if message.outreach_type == OutreachType.EMAIL:
                success = await email_service.send_email(
                    to_email=lead.email,
                    subject=message.subject,
                    body=message.content,
                    is_html=False,
                    lead_id=lead.id,
                    db=db
                )

                if success:
                    message.status = OutreachStatus.SENT
                    message.sent_at = datetime.utcnow()

                    # Update lead status
                    lead.last_contact_date = datetime.utcnow()
                    if lead.status == LeadStatus.NEW:
                        lead.status = LeadStatus.CONTACTED

                    db.commit()
                    return True

            return False

        except Exception as e:
            message.status = OutreachStatus.FAILED
            message.error_message = str(e)
            message.retry_count += 1
            db.commit()
            print(f"Error sending outreach message: {str(e)}")
            return False

    async def create_sequence(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        user_id: int,
        segment_id: Optional[int] = None,
        target_filters: Optional[Dict] = None,
        db: Session = None
    ) -> OutreachSequence:
        """Create a new outreach sequence"""

        sequence = OutreachSequence(
            user_id=user_id,
            name=name,
            description=description,
            sequence_steps=steps,
            segment_id=segment_id,
            target_filters=target_filters,
            status=SequenceStatus.DRAFT
        )

        db.add(sequence)
        db.commit()
        db.refresh(sequence)
        return sequence

    async def enroll_leads_in_sequence(
        self,
        sequence_id: int,
        lead_ids: List[int],
        db: Session
    ) -> Dict[str, int]:
        """Enroll multiple leads into a sequence"""

        results = {"enrolled": 0, "skipped": 0, "errors": 0}

        sequence = db.query(OutreachSequence).filter(
            OutreachSequence.id == sequence_id
        ).first()

        if not sequence:
            raise Exception(f"Sequence {sequence_id} not found")

        for lead_id in lead_ids:
            try:
                lead = db.query(Lead).filter(Lead.id == lead_id).first()

                if not lead:
                    results["errors"] += 1
                    continue

                # Check if already enrolled
                existing = db.query(OutreachEnrollment).filter(
                    and_(
                        OutreachEnrollment.sequence_id == sequence_id,
                        OutreachEnrollment.lead_id == lead_id,
                        OutreachEnrollment.status == "active"
                    )
                ).first()

                if existing:
                    results["skipped"] += 1
                    continue

                # Check consent
                if not lead.email_consent:
                    results["skipped"] += 1
                    continue

                # Create enrollment
                enrollment = OutreachEnrollment(
                    sequence_id=sequence_id,
                    lead_id=lead_id,
                    status="active",
                    current_step=0,
                    next_send_at=datetime.utcnow()  # Send first message immediately
                )

                db.add(enrollment)
                results["enrolled"] += 1

            except Exception as e:
                print(f"Error enrolling lead {lead_id}: {str(e)}")
                results["errors"] += 1

        # Update sequence stats
        sequence.total_enrolled += results["enrolled"]
        db.commit()

        return results

    async def process_sequence_step(
        self,
        enrollment: OutreachEnrollment,
        db: Session
    ) -> bool:
        """Process the next step in a sequence for an enrollment"""

        try:
            sequence = db.query(OutreachSequence).filter(
                OutreachSequence.id == enrollment.sequence_id
            ).first()

            lead = db.query(Lead).filter(
                Lead.id == enrollment.lead_id
            ).first()

            if not sequence or not lead:
                return False

            # Check if sequence should stop
            if sequence.stop_on_reply and enrollment.stop_reason == "replied":
                enrollment.status = "stopped"
                enrollment.stopped_at = datetime.utcnow()
                db.commit()
                return False

            # Get current step
            steps = sequence.sequence_steps
            if enrollment.current_step >= len(steps):
                # Sequence completed
                enrollment.status = "completed"
                enrollment.completed_at = datetime.utcnow()
                sequence.total_completed += 1
                db.commit()
                return False

            step = steps[enrollment.current_step]

            # Generate personalized message for this step
            message_data = await self.generate_personalized_message(
                lead=lead,
                message_type=step.get("message_type", "intro"),
                template=step.get("template"),
                additional_context=step.get("context")
            )

            # Create outreach message
            message = OutreachMessage(
                user_id=sequence.user_id,
                lead_id=lead.id,
                sequence_id=sequence.id,
                outreach_type=step.get("type", OutreachType.EMAIL),
                subject=step.get("subject") or message_data.get("subject"),
                content=message_data.get("body"),
                personalization_data=message_data.get("personalization_tokens"),
                status=OutreachStatus.SCHEDULED,
                scheduled_at=enrollment.next_send_at
            )

            db.add(message)

            # Send message
            success = await self.send_outreach_message(message, lead, db)

            if success:
                # Update enrollment for next step
                enrollment.current_step += 1

                # Calculate next send time
                if enrollment.current_step < len(steps):
                    next_step = steps[enrollment.current_step]
                    delay_days = next_step.get("delay_days", 3)
                    enrollment.next_send_at = datetime.utcnow() + timedelta(days=delay_days)

                # Update sequence stats
                sequence.total_sent += 1

                db.commit()
                return True

            return False

        except Exception as e:
            print(f"Error processing sequence step: {str(e)}")
            return False

    async def process_pending_sequences(self, db: Session) -> Dict[str, int]:
        """Process all pending sequence steps (called by scheduler)"""

        results = {"processed": 0, "failed": 0}

        # Find all active enrollments due for next step
        enrollments = db.query(OutreachEnrollment).filter(
            and_(
                OutreachEnrollment.status == "active",
                OutreachEnrollment.next_send_at <= datetime.utcnow()
            )
        ).all()

        for enrollment in enrollments:
            try:
                success = await self.process_sequence_step(enrollment, db)
                if success:
                    results["processed"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                print(f"Error processing enrollment {enrollment.id}: {str(e)}")
                results["failed"] += 1

        return results

    def get_sequence_analytics(
        self,
        sequence_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get analytics for a sequence"""

        sequence = db.query(OutreachSequence).filter(
            OutreachSequence.id == sequence_id
        ).first()

        if not sequence:
            raise Exception(f"Sequence {sequence_id} not found")

        # Calculate rates
        open_rate = (sequence.total_opened / sequence.total_sent * 100) if sequence.total_sent > 0 else 0
        click_rate = (sequence.total_clicked / sequence.total_sent * 100) if sequence.total_sent > 0 else 0
        reply_rate = (sequence.total_replied / sequence.total_sent * 100) if sequence.total_sent > 0 else 0
        completion_rate = (sequence.total_completed / sequence.total_enrolled * 100) if sequence.total_enrolled > 0 else 0

        # Get enrollment status breakdown
        enrollments = db.query(OutreachEnrollment).filter(
            OutreachEnrollment.sequence_id == sequence_id
        ).all()

        status_counts = {
            "active": len([e for e in enrollments if e.status == "active"]),
            "completed": len([e for e in enrollments if e.status == "completed"]),
            "stopped": len([e for e in enrollments if e.status == "stopped"]),
            "failed": len([e for e in enrollments if e.status == "failed"])
        }

        return {
            "sequence_id": sequence_id,
            "name": sequence.name,
            "status": sequence.status,
            "total_enrolled": sequence.total_enrolled,
            "total_sent": sequence.total_sent,
            "total_opened": sequence.total_opened,
            "total_clicked": sequence.total_clicked,
            "total_replied": sequence.total_replied,
            "total_completed": sequence.total_completed,
            "open_rate": round(open_rate, 2),
            "click_rate": round(click_rate, 2),
            "reply_rate": round(reply_rate, 2),
            "completion_rate": round(completion_rate, 2),
            "enrollment_status": status_counts,
            "created_at": sequence.created_at.isoformat() if sequence.created_at else None,
            "started_at": sequence.started_at.isoformat() if sequence.started_at else None
        }

    async def stop_sequence_for_lead(
        self,
        sequence_id: int,
        lead_id: int,
        reason: str,
        db: Session
    ) -> bool:
        """Stop a sequence for a specific lead"""

        enrollment = db.query(OutreachEnrollment).filter(
            and_(
                OutreachEnrollment.sequence_id == sequence_id,
                OutreachEnrollment.lead_id == lead_id,
                OutreachEnrollment.status == "active"
            )
        ).first()

        if not enrollment:
            return False

        enrollment.status = "stopped"
        enrollment.stopped_at = datetime.utcnow()
        enrollment.stop_reason = reason

        db.commit()
        return True


# Singleton instance
outreach_service = OutreachService()
