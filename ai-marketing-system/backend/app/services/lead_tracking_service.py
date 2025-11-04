from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import json

from app.models.lead import Lead
from app.models.lead_tracking import (
    LeadLifecycle, LeadScore, EngagementHistory,
    LeadAttribution, LeadJourney, LeadActivitySummary,
    LeadStage, EngagementType, AttributionModel
)


class LeadTrackingService:
    """Service for lead lifecycle tracking, scoring, and attribution"""

    def __init__(self):
        pass

    # ============= Lifecycle Management =============

    def transition_lead_stage(
        self,
        lead: Lead,
        new_stage: str,
        reason: Optional[str] = None,
        triggered_by: Optional[str] = None,
        db: Session = None
    ) -> LeadLifecycle:
        """Transition a lead to a new lifecycle stage"""

        # Get current stage if exists
        current_lifecycle = db.query(LeadLifecycle).filter(
            and_(
                LeadLifecycle.lead_id == lead.id,
                LeadLifecycle.is_current_stage == True
            )
        ).first()

        # Calculate duration in previous stage
        if current_lifecycle:
            current_lifecycle.exited_at = datetime.utcnow()
            current_lifecycle.is_current_stage = False
            duration = (datetime.utcnow() - current_lifecycle.entered_at).days
            current_lifecycle.duration_days = duration

        # Create new lifecycle entry
        new_lifecycle = LeadLifecycle(
            lead_id=lead.id,
            stage=new_stage,
            previous_stage=current_lifecycle.stage if current_lifecycle else None,
            entered_at=datetime.utcnow(),
            transition_reason=reason,
            triggered_by=triggered_by,
            is_current_stage=True,
            touchpoints_count=0,
            engagement_score=0
        )

        db.add(new_lifecycle)

        # Update lead status
        lead.status = new_stage

        # Update lead journey
        self._update_lead_journey(lead, db)

        db.commit()
        db.refresh(new_lifecycle)

        return new_lifecycle

    def get_lead_lifecycle_history(
        self,
        lead_id: int,
        db: Session
    ) -> List[LeadLifecycle]:
        """Get complete lifecycle history for a lead"""

        return db.query(LeadLifecycle).filter(
            LeadLifecycle.lead_id == lead_id
        ).order_by(LeadLifecycle.entered_at.desc()).all()

    def get_current_stage(
        self,
        lead_id: int,
        db: Session
    ) -> Optional[LeadLifecycle]:
        """Get current lifecycle stage for a lead"""

        return db.query(LeadLifecycle).filter(
            and_(
                LeadLifecycle.lead_id == lead_id,
                LeadLifecycle.is_current_stage == True
            )
        ).first()

    # ============= Lead Scoring =============

    def calculate_lead_score(
        self,
        lead: Lead,
        db: Session
    ) -> LeadScore:
        """Calculate comprehensive lead score"""

        # Get or create lead score record
        lead_score = db.query(LeadScore).filter(
            LeadScore.lead_id == lead.id
        ).first()

        if not lead_score:
            lead_score = LeadScore(lead_id=lead.id)
            db.add(lead_score)
        else:
            # Store previous score
            lead_score.previous_score = lead_score.total_score

        # Calculate demographic score (0-100)
        demographic_score = self._calculate_demographic_score(lead)

        # Calculate behavioral score (0-100)
        behavioral_score = self._calculate_behavioral_score(lead, db)

        # Calculate firmographic score (0-100)
        firmographic_score = self._calculate_firmographic_score(lead)

        # Calculate engagement score (0-100)
        engagement_score = self._calculate_engagement_score(lead, db)

        # Calculate intent score (0-100)
        intent_score = self._calculate_intent_score(lead, db)

        # Update component scores
        lead_score.demographic_score = demographic_score
        lead_score.behavioral_score = behavioral_score
        lead_score.firmographic_score = firmographic_score
        lead_score.engagement_score = engagement_score
        lead_score.intent_score = intent_score

        # Calculate weighted total score
        total_score = int(
            (demographic_score * 0.20) +
            (behavioral_score * 0.25) +
            (firmographic_score * 0.15) +
            (engagement_score * 0.25) +
            (intent_score * 0.15)
        )

        lead_score.total_score = total_score

        # Determine grade
        if total_score >= 90:
            lead_score.grade = "A+"
        elif total_score >= 80:
            lead_score.grade = "A"
        elif total_score >= 70:
            lead_score.grade = "B+"
        elif total_score >= 60:
            lead_score.grade = "B"
        elif total_score >= 50:
            lead_score.grade = "C+"
        elif total_score >= 40:
            lead_score.grade = "C"
        else:
            lead_score.grade = "D"

        # Determine temperature
        if total_score >= 75:
            lead_score.temperature = "hot"
        elif total_score >= 50:
            lead_score.temperature = "warm"
        else:
            lead_score.temperature = "cold"

        # Track score change
        if lead_score.previous_score:
            lead_score.score_change_amount = total_score - lead_score.previous_score
            lead_score.score_changed = lead_score.score_change_amount != 0
        else:
            lead_score.score_change_amount = 0
            lead_score.score_changed = False

        # Store score factors
        lead_score.score_factors = {
            "demographic": demographic_score,
            "behavioral": behavioral_score,
            "firmographic": firmographic_score,
            "engagement": engagement_score,
            "intent": intent_score,
            "weights": {
                "demographic": 0.20,
                "behavioral": 0.25,
                "firmographic": 0.15,
                "engagement": 0.25,
                "intent": 0.15
            }
        }

        lead_score.last_calculated_at = datetime.utcnow()
        lead_score.last_activity_date = lead.last_contact_date or lead.created_at

        db.commit()
        db.refresh(lead_score)

        # Update lead engagement score
        lead.engagement_score = total_score
        db.commit()

        return lead_score

    def _calculate_demographic_score(self, lead: Lead) -> int:
        """Calculate demographic fit score based on profile completeness"""
        score = 0

        # Profile completeness
        if lead.email:
            score += 15
        if lead.first_name:
            score += 10
        if lead.last_name:
            score += 10
        if lead.phone:
            score += 15
        if lead.location:
            score += 10

        # Customer type defined
        if lead.customer_type:
            score += 20

        # Sport type defined (business context)
        if lead.sport_type:
            score += 10

        # Interests defined
        if lead.interests:
            score += 10

        return min(score, 100)

    def _calculate_behavioral_score(self, lead: Lead, db: Session) -> int:
        """Calculate behavioral score based on past actions"""
        score = 0

        # Get engagement history
        recent_engagements = db.query(EngagementHistory).filter(
            and_(
                EngagementHistory.lead_id == lead.id,
                EngagementHistory.engaged_at >= datetime.utcnow() - timedelta(days=90)
            )
        ).all()

        if not recent_engagements:
            return 0

        # Score based on engagement types
        for engagement in recent_engagements:
            if engagement.engagement_type == EngagementType.EMAIL_OPENED:
                score += 2
            elif engagement.engagement_type == EngagementType.EMAIL_CLICKED:
                score += 5
            elif engagement.engagement_type == EngagementType.EMAIL_REPLIED:
                score += 10
            elif engagement.engagement_type == EngagementType.FORM_SUBMITTED:
                score += 15
            elif engagement.engagement_type == EngagementType.PAGE_VIEWED:
                score += 1
            elif engagement.engagement_type == EngagementType.CONTENT_DOWNLOADED:
                score += 8
            elif engagement.engagement_type == EngagementType.MEETING_SCHEDULED:
                score += 20
            elif engagement.engagement_type == EngagementType.PURCHASE_MADE:
                score += 50

        # Engagement frequency bonus
        if len(recent_engagements) > 10:
            score += 10
        elif len(recent_engagements) > 5:
            score += 5

        return min(score, 100)

    def _calculate_firmographic_score(self, lead: Lead) -> int:
        """Calculate firmographic fit score (company/business fit)"""
        score = 50  # Base score

        # Location-based scoring (if target markets defined)
        if lead.location:
            # Adjust based on target markets
            target_locations = ["United States", "Canada", "United Kingdom", "Australia"]
            if any(loc in lead.location for loc in target_locations):
                score += 20

        # Customer type fit
        if lead.customer_type in ["coach", "team"]:
            score += 15  # Higher value customers
        elif lead.customer_type == "bike_fitter":
            score += 10
        elif lead.customer_type == "athlete":
            score += 5

        # Source quality
        if lead.source in ["referral", "partner", "shopify"]:
            score += 15  # High quality sources
        elif lead.source in ["facebook_lead_ads", "form_submission"]:
            score += 10
        elif lead.source in ["import", "manual"]:
            score += 5

        return min(score, 100)

    def _calculate_engagement_score(self, lead: Lead, db: Session) -> int:
        """Calculate recent engagement score"""
        score = 0

        # Recency of contact
        if lead.last_contact_date:
            days_since_contact = (datetime.utcnow() - lead.last_contact_date).days
            if days_since_contact < 7:
                score += 40
            elif days_since_contact < 30:
                score += 30
            elif days_since_contact < 90:
                score += 20
            else:
                score += 10

        # Consent status
        if lead.email_consent:
            score += 30
        if lead.sms_consent:
            score += 15

        # Current stage
        current_stage = lead.status or "new"
        stage_scores = {
            "customer": 100,
            "opportunity": 80,
            "engaged": 60,
            "qualified": 50,
            "contacted": 30,
            "new": 15
        }
        score = max(score, stage_scores.get(current_stage, 15))

        return min(score, 100)

    def _calculate_intent_score(self, lead: Lead, db: Session) -> int:
        """Calculate purchase intent score"""
        score = 0

        # Get recent high-intent activities
        high_intent_activities = db.query(EngagementHistory).filter(
            and_(
                EngagementHistory.lead_id == lead.id,
                EngagementHistory.engaged_at >= datetime.utcnow() - timedelta(days=30),
                EngagementHistory.engagement_type.in_([
                    EngagementType.PURCHASE_MADE,
                    EngagementType.MEETING_SCHEDULED,
                    EngagementType.CONTENT_DOWNLOADED,
                    EngagementType.FORM_SUBMITTED
                ])
            )
        ).count()

        score += min(high_intent_activities * 15, 50)

        # Stage-based intent
        if lead.status == "opportunity":
            score += 40
        elif lead.status == "engaged":
            score += 30
        elif lead.status == "qualified":
            score += 20

        # Recent replies indicate intent
        recent_replies = db.query(EngagementHistory).filter(
            and_(
                EngagementHistory.lead_id == lead.id,
                EngagementHistory.engaged_at >= datetime.utcnow() - timedelta(days=14),
                EngagementHistory.engagement_type == EngagementType.EMAIL_REPLIED
            )
        ).count()

        score += min(recent_replies * 10, 30)

        return min(score, 100)

    def apply_score_decay(
        self,
        lead_score: LeadScore,
        db: Session
    ) -> LeadScore:
        """Apply decay to lead score based on inactivity"""

        if not lead_score.last_activity_date:
            return lead_score

        days_inactive = (datetime.utcnow() - lead_score.last_activity_date).days

        if days_inactive > 0:
            decay_amount = int(days_inactive * lead_score.decay_rate)
            new_score = max(lead_score.total_score - decay_amount, 0)

            if new_score != lead_score.total_score:
                lead_score.previous_score = lead_score.total_score
                lead_score.total_score = new_score
                lead_score.score_changed = True
                lead_score.score_change_amount = new_score - lead_score.previous_score

                db.commit()
                db.refresh(lead_score)

        return lead_score

    # ============= Engagement Tracking =============

    def track_engagement(
        self,
        lead_id: int,
        engagement_type: str,
        engagement_channel: str = None,
        source_type: str = None,
        source_id: int = None,
        source_name: str = None,
        title: str = None,
        description: str = None,
        event_metadata: Dict = None,
        engagement_value: int = 0,
        revenue_attributed: float = 0.0,
        ip_address: str = None,
        user_agent: str = None,
        device_type: str = None,
        location: str = None,
        db: Session = None
    ) -> EngagementHistory:
        """Track a lead engagement event"""

        engagement = EngagementHistory(
            lead_id=lead_id,
            engagement_type=engagement_type,
            engagement_channel=engagement_channel,
            source_type=source_type,
            source_id=source_id,
            source_name=source_name,
            title=title,
            description=description,
            event_metadata=event_metadata,
            engagement_value=engagement_value,
            revenue_attributed=revenue_attributed,
            engaged_at=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            location=location
        )

        db.add(engagement)

        # Update lead's last contact date
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if lead:
            lead.last_contact_date = datetime.utcnow()

        # Update current lifecycle touchpoints count
        current_lifecycle = db.query(LeadLifecycle).filter(
            and_(
                LeadLifecycle.lead_id == lead_id,
                LeadLifecycle.is_current_stage == True
            )
        ).first()

        if current_lifecycle:
            current_lifecycle.touchpoints_count += 1

        # Update lead journey
        self._update_lead_journey(lead, db)

        db.commit()
        db.refresh(engagement)

        return engagement

    def get_engagement_history(
        self,
        lead_id: int,
        days: int = 90,
        engagement_types: List[str] = None,
        db: Session = None
    ) -> List[EngagementHistory]:
        """Get engagement history for a lead"""

        query = db.query(EngagementHistory).filter(
            and_(
                EngagementHistory.lead_id == lead_id,
                EngagementHistory.engaged_at >= datetime.utcnow() - timedelta(days=days)
            )
        )

        if engagement_types:
            query = query.filter(EngagementHistory.engagement_type.in_(engagement_types))

        return query.order_by(EngagementHistory.engaged_at.desc()).all()

    # ============= Attribution Tracking =============

    def calculate_attribution(
        self,
        lead_id: int,
        conversion_type: str,
        conversion_value: float,
        attribution_model: str = AttributionModel.LINEAR,
        db: Session = None
    ) -> LeadAttribution:
        """Calculate multi-touch attribution for a conversion"""

        # Get all touchpoints for this lead
        touchpoints = db.query(EngagementHistory).filter(
            EngagementHistory.lead_id == lead_id
        ).order_by(EngagementHistory.engaged_at.asc()).all()

        if not touchpoints:
            return None

        # Create attribution record
        attribution = LeadAttribution(
            lead_id=lead_id,
            conversion_type=conversion_type,
            conversion_value=conversion_value,
            conversion_date=datetime.utcnow(),
            attribution_model=attribution_model,
            total_touchpoints=len(touchpoints)
        )

        # First touch
        first_touch = touchpoints[0]
        attribution.first_touch_source = first_touch.source_type
        attribution.first_touch_id = first_touch.source_id
        attribution.first_touch_name = first_touch.source_name
        attribution.first_touch_date = first_touch.engaged_at

        # Last touch
        last_touch = touchpoints[-1]
        attribution.last_touch_source = last_touch.source_type
        attribution.last_touch_id = last_touch.source_id
        attribution.last_touch_name = last_touch.source_name
        attribution.last_touch_date = last_touch.engaged_at

        # Calculate journey duration
        journey_duration = (last_touch.engaged_at - first_touch.engaged_at).days
        attribution.journey_duration_days = journey_duration

        # Calculate average time between touches
        if len(touchpoints) > 1:
            total_gaps = sum(
                (touchpoints[i].engaged_at - touchpoints[i-1].engaged_at).days
                for i in range(1, len(touchpoints))
            )
            attribution.avg_time_between_touches = total_gaps / (len(touchpoints) - 1)

        # Calculate weights based on attribution model
        touchpoint_data = []

        if attribution_model == AttributionModel.FIRST_TOUCH:
            # 100% credit to first touch
            attribution.first_touch_weight = 1.0
            attribution.last_touch_weight = 0.0
            for i, tp in enumerate(touchpoints):
                weight = 1.0 if i == 0 else 0.0
                touchpoint_data.append(self._format_touchpoint(tp, weight))

        elif attribution_model == AttributionModel.LAST_TOUCH:
            # 100% credit to last touch
            attribution.first_touch_weight = 0.0
            attribution.last_touch_weight = 1.0
            for i, tp in enumerate(touchpoints):
                weight = 1.0 if i == len(touchpoints) - 1 else 0.0
                touchpoint_data.append(self._format_touchpoint(tp, weight))

        elif attribution_model == AttributionModel.LINEAR:
            # Equal credit to all touches
            weight = 1.0 / len(touchpoints)
            attribution.first_touch_weight = weight
            attribution.last_touch_weight = weight
            for tp in touchpoints:
                touchpoint_data.append(self._format_touchpoint(tp, weight))

        elif attribution_model == AttributionModel.TIME_DECAY:
            # More credit to recent touches
            weights = self._calculate_time_decay_weights(touchpoints)
            attribution.first_touch_weight = weights[0]
            attribution.last_touch_weight = weights[-1]
            for tp, weight in zip(touchpoints, weights):
                touchpoint_data.append(self._format_touchpoint(tp, weight))

        elif attribution_model == AttributionModel.U_SHAPED:
            # 40% first, 40% last, 20% distributed to middle
            if len(touchpoints) == 1:
                weights = [1.0]
            elif len(touchpoints) == 2:
                weights = [0.5, 0.5]
            else:
                middle_weight = 0.20 / (len(touchpoints) - 2)
                weights = [0.40] + [middle_weight] * (len(touchpoints) - 2) + [0.40]

            attribution.first_touch_weight = weights[0]
            attribution.last_touch_weight = weights[-1]
            for tp, weight in zip(touchpoints, weights):
                touchpoint_data.append(self._format_touchpoint(tp, weight))

        elif attribution_model == AttributionModel.W_SHAPED:
            # 30% first, 30% last, 30% opportunity creation, 10% others
            # For simplicity, treat middle point as opportunity
            if len(touchpoints) == 1:
                weights = [1.0]
            elif len(touchpoints) == 2:
                weights = [0.5, 0.5]
            elif len(touchpoints) == 3:
                weights = [0.30, 0.40, 0.30]
            else:
                middle_idx = len(touchpoints) // 2
                other_weight = 0.10 / (len(touchpoints) - 3)
                weights = [0.30] + [other_weight] * (middle_idx - 1) + [0.30] + \
                         [other_weight] * (len(touchpoints) - middle_idx - 2) + [0.30]

            attribution.first_touch_weight = weights[0]
            attribution.last_touch_weight = weights[-1]
            for tp, weight in zip(touchpoints, weights):
                touchpoint_data.append(self._format_touchpoint(tp, weight))

        attribution.touchpoints = touchpoint_data

        # Identify primary and secondary touchpoints (highest weights)
        sorted_touchpoints = sorted(
            touchpoint_data,
            key=lambda x: x['weight'],
            reverse=True
        )
        if sorted_touchpoints:
            attribution.primary_touchpoint = sorted_touchpoints[0]
        if len(sorted_touchpoints) > 1:
            attribution.secondary_touchpoint = sorted_touchpoints[1]

        db.add(attribution)
        db.commit()
        db.refresh(attribution)

        return attribution

    def _format_touchpoint(self, touchpoint: EngagementHistory, weight: float) -> Dict:
        """Format touchpoint data for attribution"""
        return {
            "type": touchpoint.source_type,
            "id": touchpoint.source_id,
            "name": touchpoint.source_name,
            "engagement_type": touchpoint.engagement_type,
            "channel": touchpoint.engagement_channel,
            "weight": round(weight, 4),
            "date": touchpoint.engaged_at.isoformat() if touchpoint.engaged_at else None,
            "value": touchpoint.engagement_value
        }

    def _calculate_time_decay_weights(
        self,
        touchpoints: List[EngagementHistory],
        half_life_days: int = 7
    ) -> List[float]:
        """Calculate time-decay weights for touchpoints"""

        if not touchpoints:
            return []

        # Get days from first touch for each touchpoint
        first_date = touchpoints[0].engaged_at
        days_from_start = [
            (tp.engaged_at - first_date).days for tp in touchpoints
        ]

        # Calculate decay weights (exponential decay)
        import math
        decay_constant = math.log(2) / half_life_days
        raw_weights = [
            math.exp(decay_constant * days) for days in days_from_start
        ]

        # Normalize to sum to 1.0
        total_weight = sum(raw_weights)
        normalized_weights = [w / total_weight for w in raw_weights]

        return normalized_weights

    # ============= Journey Tracking =============

    def _update_lead_journey(
        self,
        lead: Lead,
        db: Session
    ) -> LeadJourney:
        """Update or create lead journey record"""

        journey = db.query(LeadJourney).filter(
            LeadJourney.lead_id == lead.id
        ).first()

        if not journey:
            journey = LeadJourney(
                lead_id=lead.id,
                journey_start_date=lead.created_at
            )
            db.add(journey)

        # Update basic metrics
        journey.last_activity_date = lead.last_contact_date or datetime.utcnow()
        journey.journey_duration_days = (
            datetime.utcnow() - journey.journey_start_date
        ).days

        # Update engagement counts
        engagements = db.query(EngagementHistory).filter(
            EngagementHistory.lead_id == lead.id
        ).all()

        journey.total_engagements = len(engagements)
        journey.email_engagements = sum(
            1 for e in engagements
            if e.engagement_channel == 'email'
        )
        journey.form_submissions = sum(
            1 for e in engagements
            if e.engagement_type == EngagementType.FORM_SUBMITTED
        )
        journey.page_views = sum(
            1 for e in engagements
            if e.engagement_type == EngagementType.PAGE_VIEWED
        )
        journey.purchases = sum(
            1 for e in engagements
            if e.engagement_type == EngagementType.PURCHASE_MADE
        )

        # Calculate days since last activity
        if journey.last_activity_date:
            journey.days_since_last_activity = (
                datetime.utcnow() - journey.last_activity_date
            ).days

        # Calculate engagement trend
        recent_engagements = [
            e for e in engagements
            if e.engaged_at >= datetime.utcnow() - timedelta(days=30)
        ]
        older_engagements = [
            e for e in engagements
            if e.engaged_at < datetime.utcnow() - timedelta(days=30) and
               e.engaged_at >= datetime.utcnow() - timedelta(days=60)
        ]

        if len(recent_engagements) > len(older_engagements):
            journey.engagement_trend = "increasing"
        elif len(recent_engagements) < len(older_engagements):
            journey.engagement_trend = "declining"
        else:
            journey.engagement_trend = "stable"

        # Calculate churn risk
        if journey.days_since_last_activity > 90:
            journey.risk_of_churn = 0.8
        elif journey.days_since_last_activity > 60:
            journey.risk_of_churn = 0.6
        elif journey.days_since_last_activity > 30:
            journey.risk_of_churn = 0.4
        else:
            journey.risk_of_churn = 0.2

        # Update current stage
        journey.current_stage = lead.status

        # Get stages completed
        lifecycle_history = db.query(LeadLifecycle).filter(
            LeadLifecycle.lead_id == lead.id
        ).order_by(LeadLifecycle.entered_at.asc()).all()

        stages_completed = [
            {
                "stage": lc.stage,
                "entered_at": lc.entered_at.isoformat() if lc.entered_at else None,
                "exited_at": lc.exited_at.isoformat() if lc.exited_at else None,
                "duration_days": lc.duration_days
            }
            for lc in lifecycle_history
        ]
        journey.stages_completed = stages_completed

        # Build milestones
        milestones = []

        # First contact
        if engagements:
            first_engagement = min(engagements, key=lambda e: e.engaged_at)
            milestones.append({
                "type": "first_contact",
                "date": first_engagement.engaged_at.isoformat(),
                "source": first_engagement.source_name
            })

        # Stage progressions
        for lc in lifecycle_history:
            if lc.stage in ["qualified", "opportunity", "customer"]:
                milestones.append({
                    "type": lc.stage,
                    "date": lc.entered_at.isoformat() if lc.entered_at else None
                })

        journey.milestones = milestones

        # Calculate revenue
        total_revenue = sum(
            e.revenue_attributed for e in engagements
            if e.revenue_attributed
        )
        journey.total_revenue = total_revenue
        journey.lifetime_value = total_revenue

        db.commit()
        db.refresh(journey)

        return journey

    def get_lead_journey(
        self,
        lead_id: int,
        db: Session
    ) -> Optional[LeadJourney]:
        """Get complete lead journey"""

        return db.query(LeadJourney).filter(
            LeadJourney.lead_id == lead_id
        ).first()

    # ============= Activity Summaries =============

    def generate_activity_summary(
        self,
        lead_id: int,
        period_type: str,
        period_start: datetime,
        period_end: datetime,
        db: Session
    ) -> LeadActivitySummary:
        """Generate activity summary for a time period"""

        # Get lead
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return None

        # Get stage at start and end
        stage_at_start = self._get_stage_at_date(lead_id, period_start, db)
        stage_at_end = self._get_stage_at_date(lead_id, period_end, db)

        # Get engagements in period
        engagements = db.query(EngagementHistory).filter(
            and_(
                EngagementHistory.lead_id == lead_id,
                EngagementHistory.engaged_at >= period_start,
                EngagementHistory.engaged_at < period_end
            )
        ).all()

        # Calculate metrics
        emails_sent = sum(1 for e in engagements if e.engagement_type == EngagementType.EMAIL_SENT)
        emails_opened = sum(1 for e in engagements if e.engagement_type == EngagementType.EMAIL_OPENED)
        emails_clicked = sum(1 for e in engagements if e.engagement_type == EngagementType.EMAIL_CLICKED)
        forms_submitted = sum(1 for e in engagements if e.engagement_type == EngagementType.FORM_SUBMITTED)
        pages_viewed = sum(1 for e in engagements if e.engagement_type == EngagementType.PAGE_VIEWED)

        # Get scores
        lead_score = db.query(LeadScore).filter(
            LeadScore.lead_id == lead_id
        ).first()

        summary = LeadActivitySummary(
            lead_id=lead_id,
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            emails_sent=emails_sent,
            emails_opened=emails_opened,
            emails_clicked=emails_clicked,
            forms_submitted=forms_submitted,
            pages_viewed=pages_viewed,
            total_engagements=len(engagements),
            period_engagement_score=lead_score.total_score if lead_score else 0,
            score_change=lead_score.score_change_amount if lead_score else 0,
            was_active=len(engagements) > 0,
            stage_at_start=stage_at_start,
            stage_at_end=stage_at_end,
            stage_changed=stage_at_start != stage_at_end
        )

        db.add(summary)
        db.commit()
        db.refresh(summary)

        return summary

    def _get_stage_at_date(
        self,
        lead_id: int,
        date: datetime,
        db: Session
    ) -> str:
        """Get lead stage at a specific date"""

        lifecycle = db.query(LeadLifecycle).filter(
            and_(
                LeadLifecycle.lead_id == lead_id,
                LeadLifecycle.entered_at <= date,
                or_(
                    LeadLifecycle.exited_at.is_(None),
                    LeadLifecycle.exited_at > date
                )
            )
        ).first()

        return lifecycle.stage if lifecycle else "new"


# Singleton instance
lead_tracking_service = LeadTrackingService()
