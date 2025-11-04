import re
import hashlib
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.lead import Lead


class LeadEnrichmentService:
    """Service for lead enrichment and deduplication"""

    def __init__(self):
        pass

    # ============= Deduplication =============

    def find_duplicates(
        self,
        db: Session,
        lead_id: Optional[int] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> List[Lead]:
        """Find duplicate leads based on email or phone"""

        if not email and not phone and not lead_id:
            return []

        # If lead_id provided, get that lead's details
        if lead_id:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return []
            email = lead.email
            phone = lead.phone

        # Build query to find duplicates
        conditions = []

        if email:
            conditions.append(Lead.email == email.lower().strip())

        if phone:
            # Normalize phone number
            normalized_phone = self._normalize_phone(phone)
            if normalized_phone:
                conditions.append(Lead.phone.like(f"%{normalized_phone}%"))

        if not conditions:
            return []

        query = db.query(Lead).filter(or_(*conditions))

        # Exclude the original lead if lead_id was provided
        if lead_id:
            query = query.filter(Lead.id != lead_id)

        duplicates = query.all()
        return duplicates

    def merge_leads(
        self,
        primary_lead_id: int,
        duplicate_lead_ids: List[int],
        db: Session
    ) -> Lead:
        """Merge duplicate leads into a primary lead"""

        primary_lead = db.query(Lead).filter(Lead.id == primary_lead_id).first()
        if not primary_lead:
            raise Exception(f"Primary lead {primary_lead_id} not found")

        duplicate_leads = db.query(Lead).filter(Lead.id.in_(duplicate_lead_ids)).all()

        # Merge data from duplicates into primary
        for dup_lead in duplicate_leads:
            # Take non-null values from duplicates if primary is null
            if not primary_lead.first_name and dup_lead.first_name:
                primary_lead.first_name = dup_lead.first_name

            if not primary_lead.last_name and dup_lead.last_name:
                primary_lead.last_name = dup_lead.last_name

            if not primary_lead.phone and dup_lead.phone:
                primary_lead.phone = dup_lead.phone

            if not primary_lead.location and dup_lead.location:
                primary_lead.location = dup_lead.location

            # Merge interests (combine and deduplicate)
            if dup_lead.interests:
                primary_interests = primary_lead.interests or ""
                combined = f"{primary_interests},{dup_lead.interests}"
                unique_interests = list(set(filter(None, combined.split(','))))
                primary_lead.interests = ','.join(unique_interests)

            # Take highest engagement score
            if dup_lead.engagement_score > primary_lead.engagement_score:
                primary_lead.engagement_score = dup_lead.engagement_score

            # Ensure consent is maintained if any duplicate has it
            if dup_lead.email_consent and not primary_lead.email_consent:
                primary_lead.email_consent = True
                primary_lead.consent_date = dup_lead.consent_date
                primary_lead.consent_source = dup_lead.consent_source

            if dup_lead.sms_consent and not primary_lead.sms_consent:
                primary_lead.sms_consent = True

            # Append notes
            if dup_lead.notes:
                current_notes = primary_lead.notes or ""
                primary_lead.notes = f"{current_notes}\n\n[Merged from lead {dup_lead.id}]: {dup_lead.notes}"

            # Delete duplicate lead
            db.delete(dup_lead)

        db.commit()
        db.refresh(primary_lead)

        return primary_lead

    def auto_deduplicate(
        self,
        db: Session,
        dry_run: bool = True
    ) -> Dict[str, any]:
        """Automatically find and merge duplicate leads"""

        # Find all duplicate groups
        duplicate_groups = []

        # Group by email
        email_groups = db.query(
            Lead.email,
            func.count(Lead.id).label('count')
        ).filter(
            Lead.email.isnot(None),
            Lead.email != ''
        ).group_by(
            Lead.email
        ).having(
            func.count(Lead.id) > 1
        ).all()

        for email, count in email_groups:
            leads = db.query(Lead).filter(Lead.email == email).all()
            if len(leads) > 1:
                # Use the oldest lead as primary
                primary = min(leads, key=lambda l: l.created_at)
                duplicates = [l.id for l in leads if l.id != primary.id]
                duplicate_groups.append({
                    'primary_id': primary.id,
                    'duplicate_ids': duplicates,
                    'match_type': 'email',
                    'match_value': email
                })

        results = {
            'total_groups': len(duplicate_groups),
            'total_duplicates': sum(len(g['duplicate_ids']) for g in duplicate_groups),
            'groups': duplicate_groups
        }

        if not dry_run:
            # Actually merge the duplicates
            merged_count = 0
            for group in duplicate_groups:
                try:
                    self.merge_leads(
                        group['primary_id'],
                        group['duplicate_ids'],
                        db
                    )
                    merged_count += 1
                except Exception as e:
                    print(f"Error merging group: {str(e)}")

            results['merged_count'] = merged_count

        return results

    # ============= Enrichment =============

    def enrich_lead(
        self,
        lead: Lead,
        db: Session
    ) -> Lead:
        """Enrich lead data with derived information"""

        # Derive name from email if missing
        if not lead.first_name and lead.email:
            email_name = lead.email.split('@')[0]
            # Try to extract first and last name from email
            parts = re.split(r'[._-]', email_name)
            if len(parts) >= 2:
                lead.first_name = parts[0].capitalize()
                lead.last_name = parts[-1].capitalize()
            elif len(parts) == 1:
                lead.first_name = parts[0].capitalize()

        # Infer location from email domain (basic)
        if not lead.location and lead.email:
            domain = lead.email.split('@')[-1].lower()
            # Common TLDs to location mapping (very basic)
            if '.uk' in domain or '.co.uk' in domain:
                lead.location = 'United Kingdom'
            elif '.ca' in domain:
                lead.location = 'Canada'
            elif '.au' in domain:
                lead.location = 'Australia'
            elif '.de' in domain:
                lead.location = 'Germany'
            elif '.fr' in domain:
                lead.location = 'France'

        # Calculate engagement score based on available data
        lead.engagement_score = self._calculate_engagement_score(lead, db)

        # Infer customer type from interests or sport type
        if not lead.customer_type:
            interests_lower = (lead.interests or '').lower()
            if 'coach' in interests_lower:
                lead.customer_type = 'coach'
            elif 'team' in interests_lower:
                lead.customer_type = 'team'
            elif 'fitter' in interests_lower or 'fitting' in interests_lower:
                lead.customer_type = 'bike_fitter'
            else:
                lead.customer_type = 'athlete'

        db.commit()
        db.refresh(lead)

        return lead

    def bulk_enrich(
        self,
        db: Session,
        lead_ids: Optional[List[int]] = None
    ) -> Dict[str, int]:
        """Enrich multiple leads at once"""

        if lead_ids:
            leads = db.query(Lead).filter(Lead.id.in_(lead_ids)).all()
        else:
            # Enrich all leads
            leads = db.query(Lead).all()

        enriched_count = 0
        for lead in leads:
            try:
                self.enrich_lead(lead, db)
                enriched_count += 1
            except Exception as e:
                print(f"Error enriching lead {lead.id}: {str(e)}")

        return {
            'total_leads': len(leads),
            'enriched_count': enriched_count
        }

    def _calculate_engagement_score(
        self,
        lead: Lead,
        db: Session
    ) -> int:
        """Calculate engagement score for a lead (0-100)"""

        score = 0

        # Base score for having email
        if lead.email:
            score += 10

        # Score for consent
        if lead.email_consent:
            score += 20
        if lead.sms_consent:
            score += 10

        # Score for complete profile
        if lead.first_name:
            score += 5
        if lead.last_name:
            score += 5
        if lead.phone:
            score += 10
        if lead.location:
            score += 5

        # Score for interests
        if lead.interests:
            interest_count = len((lead.interests or '').split(','))
            score += min(interest_count * 3, 15)

        # Score for recent activity
        if lead.last_contact_date:
            from datetime import datetime, timedelta
            days_since_contact = (datetime.utcnow() - lead.last_contact_date).days
            if days_since_contact < 7:
                score += 20
            elif days_since_contact < 30:
                score += 10
            elif days_since_contact < 90:
                score += 5

        # Cap at 100
        return min(score, 100)

    # ============= Validation & Cleaning =============

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_phone(self, phone: str) -> bool:
        """Validate phone format (basic)"""
        # Remove all non-numeric characters
        digits = re.sub(r'\D', '', phone)
        # Should have at least 10 digits
        return len(digits) >= 10

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to digits only"""
        if not phone:
            return ''
        return re.sub(r'\D', '', phone)

    def clean_lead_data(
        self,
        lead: Lead,
        db: Session
    ) -> Lead:
        """Clean and standardize lead data"""

        # Clean email
        if lead.email:
            lead.email = lead.email.lower().strip()
            if not self.validate_email(lead.email):
                lead.email = None

        # Clean phone
        if lead.phone:
            if self.validate_phone(lead.phone):
                lead.phone = self._normalize_phone(lead.phone)
            else:
                lead.phone = None

        # Clean names
        if lead.first_name:
            lead.first_name = lead.first_name.strip().title()

        if lead.last_name:
            lead.last_name = lead.last_name.strip().title()

        # Clean location
        if lead.location:
            lead.location = lead.location.strip().title()

        db.commit()
        db.refresh(lead)

        return lead

    # ============= Lead Quality Scoring =============

    def calculate_lead_quality(
        self,
        lead: Lead,
        db: Session
    ) -> Dict[str, any]:
        """Calculate comprehensive lead quality score"""

        scores = {
            'completeness': 0,  # How complete is the profile
            'engagement': lead.engagement_score or 0,
            'consent': 0,  # Consent status
            'recency': 0,  # How recent is the lead
            'quality': 0  # Overall quality score
        }

        # Completeness score (0-100)
        fields = ['email', 'first_name', 'last_name', 'phone', 'location', 'sport_type', 'customer_type']
        filled_fields = sum(1 for field in fields if getattr(lead, field))
        scores['completeness'] = int((filled_fields / len(fields)) * 100)

        # Consent score (0-100)
        consent_score = 0
        if lead.email_consent:
            consent_score += 60
        if lead.sms_consent:
            consent_score += 40
        scores['consent'] = consent_score

        # Recency score (0-100)
        from datetime import datetime, timedelta
        days_old = (datetime.utcnow() - lead.created_at).days
        if days_old < 7:
            scores['recency'] = 100
        elif days_old < 30:
            scores['recency'] = 80
        elif days_old < 90:
            scores['recency'] = 60
        elif days_old < 180:
            scores['recency'] = 40
        else:
            scores['recency'] = 20

        # Overall quality (weighted average)
        scores['quality'] = int(
            (scores['completeness'] * 0.3) +
            (scores['engagement'] * 0.3) +
            (scores['consent'] * 0.25) +
            (scores['recency'] * 0.15)
        )

        # Classification
        if scores['quality'] >= 80:
            quality_tier = 'A (Hot Lead)'
        elif scores['quality'] >= 60:
            quality_tier = 'B (Warm Lead)'
        elif scores['quality'] >= 40:
            quality_tier = 'C (Cold Lead)'
        else:
            quality_tier = 'D (Low Quality)'

        return {
            **scores,
            'tier': quality_tier
        }


# Singleton instance
lead_enrichment_service = LeadEnrichmentService()
