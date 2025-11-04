import httpx
import hashlib
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.retargeting import (
    RetargetingAudience, RetargetingEvent, RetargetingCampaign,
    RetargetingPerformance, AudienceStatus
)
from app.models.lead import Lead
from app.core.config import settings


class RetargetingService:
    """Service for managing retargeting audiences and campaigns across Meta and Google"""

    def __init__(self):
        self.meta_access_token = getattr(settings, 'META_ACCESS_TOKEN', None)
        self.meta_business_account_id = getattr(settings, 'META_BUSINESS_ACCOUNT_ID', None)
        self.google_ads_customer_id = getattr(settings, 'GOOGLE_ADS_CUSTOMER_ID', None)
        self.meta_pixel_id = getattr(settings, 'META_PIXEL_ID', None)
        self.ga4_measurement_id = getattr(settings, 'GA4_MEASUREMENT_ID', None)

    # ============= Audience Management =============

    async def create_audience(
        self,
        name: str,
        description: str,
        platform: str,
        criteria: Dict[str, Any],
        user_id: int,
        db: Session
    ) -> RetargetingAudience:
        """Create a new retargeting audience"""

        audience = RetargetingAudience(
            user_id=user_id,
            name=name,
            description=description,
            platform=platform,
            criteria=criteria,
            status=AudienceStatus.DRAFT
        )

        db.add(audience)
        db.commit()
        db.refresh(audience)

        return audience

    async def sync_audience_to_platform(
        self,
        audience: RetargetingAudience,
        db: Session
    ) -> bool:
        """Sync audience to Meta or Google Ads platform"""

        try:
            audience.status = AudienceStatus.SYNCING
            db.commit()

            # Get leads matching audience criteria
            leads = self._get_leads_for_audience(audience, db)

            if audience.platform in ['meta', 'both']:
                success = await self._sync_to_meta(audience, leads, db)
                if not success:
                    raise Exception("Failed to sync to Meta")

            if audience.platform in ['google', 'both']:
                success = await self._sync_to_google(audience, leads, db)
                if not success:
                    raise Exception("Failed to sync to Google")

            audience.status = AudienceStatus.ACTIVE
            audience.actual_size = len(leads)
            audience.last_sync_at = datetime.utcnow()
            audience.synced_at = datetime.utcnow()
            audience.sync_attempts += 1
            db.commit()

            return True

        except Exception as e:
            audience.status = AudienceStatus.ERROR
            audience.error_message = str(e)
            audience.sync_attempts += 1
            db.commit()
            print(f"Error syncing audience: {str(e)}")
            return False

    async def _sync_to_meta(
        self,
        audience: RetargetingAudience,
        leads: List[Lead],
        db: Session
    ) -> bool:
        """Sync audience to Meta (Facebook/Instagram) Custom Audience"""

        if not self.meta_access_token or not self.meta_business_account_id:
            print("Meta credentials not configured")
            return False

        try:
            # Prepare user data for Custom Audience
            # Hash emails and phones according to Meta requirements
            user_data = []
            for lead in leads:
                user_entry = {}

                if lead.email:
                    user_entry['em'] = self._hash_for_meta(lead.email.lower().strip())

                if lead.phone:
                    # Remove non-numeric characters
                    phone = ''.join(filter(str.isdigit, lead.phone))
                    user_entry['ph'] = self._hash_for_meta(phone)

                if lead.first_name:
                    user_entry['fn'] = self._hash_for_meta(lead.first_name.lower().strip())

                if lead.last_name:
                    user_entry['ln'] = self._hash_for_meta(lead.last_name.lower().strip())

                if user_entry:
                    user_data.append(user_entry)

            # Create or update Custom Audience via Meta API
            base_url = "https://graph.facebook.com/v18.0"

            if audience.meta_audience_id:
                # Update existing audience
                url = f"{base_url}/{audience.meta_audience_id}/users"

                # Split into batches of 10,000 (Meta limit)
                batch_size = 10000
                for i in range(0, len(user_data), batch_size):
                    batch = user_data[i:i + batch_size]

                    payload = {
                        "payload": {
                            "schema": ["EMAIL_SHA256", "PHONE_SHA256", "FN_SHA256", "LN_SHA256"],
                            "data": [[
                                entry.get('em', ''),
                                entry.get('ph', ''),
                                entry.get('fn', ''),
                                entry.get('ln', '')
                            ] for entry in batch]
                        }
                    }

                    async with httpx.AsyncClient(timeout=60.0) as client:
                        response = await client.post(
                            url,
                            params={"access_token": self.meta_access_token},
                            json=payload
                        )
                        response.raise_for_status()

            else:
                # Create new Custom Audience
                url = f"{base_url}/act_{self.meta_business_account_id}/customaudiences"

                payload = {
                    "name": audience.name,
                    "description": audience.description or "",
                    "subtype": "CUSTOM",
                    "customer_file_source": "USER_PROVIDED_ONLY"
                }

                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        url,
                        params={"access_token": self.meta_access_token},
                        json=payload
                    )
                    response.raise_for_status()
                    result = response.json()

                    audience.meta_audience_id = result.get('id')
                    db.commit()

                    # Add users to newly created audience
                    if user_data:
                        users_url = f"{base_url}/{audience.meta_audience_id}/users"

                        # Split into batches
                        batch_size = 10000
                        for i in range(0, len(user_data), batch_size):
                            batch = user_data[i:i + batch_size]

                            users_payload = {
                                "payload": {
                                    "schema": ["EMAIL_SHA256", "PHONE_SHA256", "FN_SHA256", "LN_SHA256"],
                                    "data": [[
                                        entry.get('em', ''),
                                        entry.get('ph', ''),
                                        entry.get('fn', ''),
                                        entry.get('ln', '')
                                    ] for entry in batch]
                                }
                            }

                            response = await client.post(
                                users_url,
                                params={"access_token": self.meta_access_token},
                                json=users_payload
                            )
                            response.raise_for_status()

            return True

        except Exception as e:
            print(f"Error syncing to Meta: {str(e)}")
            return False

    async def _sync_to_google(
        self,
        audience: RetargetingAudience,
        leads: List[Lead],
        db: Session
    ) -> bool:
        """Sync audience to Google Ads Customer Match"""

        if not self.google_ads_customer_id:
            print("Google Ads credentials not configured")
            return False

        try:
            # Note: Google Ads API requires OAuth2 and more complex setup
            # This is a simplified placeholder for the integration

            # Prepare user data
            user_data = []
            for lead in leads:
                user_entry = {
                    "hashedEmail": self._hash_for_google(lead.email.lower().strip()) if lead.email else None,
                    "hashedPhoneNumber": self._hash_for_google(''.join(filter(str.isdigit, lead.phone))) if lead.phone else None,
                    "addressInfo": {
                        "hashedFirstName": self._hash_for_google(lead.first_name.lower().strip()) if lead.first_name else None,
                        "hashedLastName": self._hash_for_google(lead.last_name.lower().strip()) if lead.last_name else None
                    }
                }
                user_data.append(user_entry)

            # Store Google audience ID (actual API call would go here)
            if not audience.google_audience_id:
                # Placeholder for Google Ads API audience creation
                audience.google_audience_id = f"google_audience_{audience.id}"
                db.commit()

            print(f"Would sync {len(user_data)} users to Google Ads Customer Match")
            return True

        except Exception as e:
            print(f"Error syncing to Google: {str(e)}")
            return False

    def _get_leads_for_audience(
        self,
        audience: RetargetingAudience,
        db: Session
    ) -> List[Lead]:
        """Get leads matching audience criteria"""

        criteria = audience.criteria or {}

        # Start with base query - only leads with email consent
        query = db.query(Lead).filter(Lead.email_consent == True)

        # Apply criteria filters
        if criteria.get('sport_type'):
            query = query.filter(Lead.sport_type == criteria['sport_type'])

        if criteria.get('customer_type'):
            query = query.filter(Lead.customer_type == criteria['customer_type'])

        if criteria.get('status'):
            query = query.filter(Lead.status == criteria['status'])

        if criteria.get('min_engagement_score'):
            query = query.filter(Lead.engagement_score >= criteria['min_engagement_score'])

        # Date range filter
        if criteria.get('created_after'):
            created_after = datetime.fromisoformat(criteria['created_after'])
            query = query.filter(Lead.created_at >= created_after)

        # Get events-based criteria
        event_types = criteria.get('events', [])
        timeframe_days = criteria.get('timeframe_days', 30)

        if event_types:
            # Filter leads who have performed specific events
            cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)

            # Get lead IDs from events
            event_lead_ids = db.query(RetargetingEvent.lead_id).filter(
                and_(
                    RetargetingEvent.event_type.in_(event_types),
                    RetargetingEvent.event_time >= cutoff_date,
                    RetargetingEvent.lead_id.isnot(None)
                )
            ).distinct()

            query = query.filter(Lead.id.in_(event_lead_ids))

        # Exclude recent purchasers if specified
        if criteria.get('exclude_purchasers'):
            exclude_days = criteria.get('exclude_purchase_days', 30)
            cutoff_date = datetime.utcnow() - timedelta(days=exclude_days)

            purchaser_ids = db.query(RetargetingEvent.lead_id).filter(
                and_(
                    RetargetingEvent.event_type == 'purchase',
                    RetargetingEvent.event_time >= cutoff_date,
                    RetargetingEvent.lead_id.isnot(None)
                )
            ).distinct()

            query = query.filter(~Lead.id.in_(purchaser_ids))

        leads = query.all()
        return leads

    def _hash_for_meta(self, value: str) -> str:
        """Hash value using SHA256 for Meta"""
        return hashlib.sha256(value.encode()).hexdigest()

    def _hash_for_google(self, value: str) -> str:
        """Hash value using SHA256 for Google"""
        return hashlib.sha256(value.encode()).hexdigest()

    # ============= Event Tracking =============

    async def track_event(
        self,
        event_type: str,
        event_name: str,
        platform: str,
        event_data: Dict[str, Any],
        user_identifier: Optional[str] = None,
        lead_id: Optional[int] = None,
        db: Session = None
    ) -> RetargetingEvent:
        """Track a retargeting event"""

        event = RetargetingEvent(
            event_type=event_type,
            event_name=event_name,
            platform=platform,
            event_data=event_data,
            user_identifier=user_identifier,
            lead_id=lead_id,
            conversion_value=event_data.get('value'),
            currency=event_data.get('currency', 'USD'),
            session_id=event_data.get('session_id'),
            ip_address=event_data.get('ip_address'),
            user_agent=event_data.get('user_agent')
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        # Send event to pixels
        if platform in ['meta', 'website']:
            await self._send_event_to_meta_pixel(event)

        if platform in ['google', 'website']:
            await self._send_event_to_ga4(event)

        return event

    async def _send_event_to_meta_pixel(self, event: RetargetingEvent) -> bool:
        """Send conversion event to Meta Pixel via Conversions API"""

        if not self.meta_access_token or not self.meta_pixel_id:
            return False

        try:
            url = f"https://graph.facebook.com/v18.0/{self.meta_pixel_id}/events"

            # Build event data
            event_data = {
                "event_name": event.event_name or event.event_type,
                "event_time": int(event.event_time.timestamp()),
                "action_source": "website",
                "user_data": {}
            }

            # Add user data
            if event.user_identifier:
                if '@' in event.user_identifier:
                    event_data["user_data"]["em"] = self._hash_for_meta(event.user_identifier.lower())
                else:
                    event_data["user_data"]["ph"] = self._hash_for_meta(event.user_identifier)

            if event.ip_address:
                event_data["user_data"]["client_ip_address"] = event.ip_address

            if event.user_agent:
                event_data["user_data"]["client_user_agent"] = event.user_agent

            # Add custom data
            if event.event_data:
                event_data["custom_data"] = {
                    "value": event.conversion_value,
                    "currency": event.currency
                }

            payload = {
                "data": [event_data],
                "access_token": self.meta_access_token
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

            return True

        except Exception as e:
            print(f"Error sending event to Meta Pixel: {str(e)}")
            return False

    async def _send_event_to_ga4(self, event: RetargetingEvent) -> bool:
        """Send event to Google Analytics 4 via Measurement Protocol"""

        if not self.ga4_measurement_id:
            return False

        try:
            # GA4 Measurement Protocol endpoint
            url = f"https://www.google-analytics.com/mp/collect"

            params = {
                "measurement_id": self.ga4_measurement_id,
                "api_secret": getattr(settings, 'GA4_API_SECRET', '')  # Need to configure
            }

            payload = {
                "client_id": event.session_id or event.user_identifier or "unknown",
                "events": [{
                    "name": event.event_name or event.event_type,
                    "params": {
                        "value": event.conversion_value,
                        "currency": event.currency,
                        **event.event_data
                    }
                }]
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, params=params, json=payload)
                response.raise_for_status()

            return True

        except Exception as e:
            print(f"Error sending event to GA4: {str(e)}")
            return False

    # ============= Campaign Management =============

    async def create_campaign(
        self,
        name: str,
        audience_id: int,
        platform: str,
        ad_creative: Dict[str, Any],
        budget_daily: float,
        user_id: int,
        db: Session
    ) -> RetargetingCampaign:
        """Create a new retargeting campaign"""

        campaign = RetargetingCampaign(
            user_id=user_id,
            audience_id=audience_id,
            name=name,
            platform=platform,
            ad_creative=ad_creative,
            budget_daily=budget_daily,
            status='draft'
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        return campaign

    def get_audience_analytics(
        self,
        audience_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get analytics for an audience"""

        audience = db.query(RetargetingAudience).filter(
            RetargetingAudience.id == audience_id
        ).first()

        if not audience:
            raise Exception(f"Audience {audience_id} not found")

        # Get event counts
        events = db.query(RetargetingEvent).filter(
            RetargetingEvent.audience_id == audience_id
        ).all()

        total_events = len(events)

        # Count by event type
        events_by_type = {}
        for event in events:
            event_type = event.event_type
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

        # Top conversions
        top_conversions = db.query(
            RetargetingEvent.event_name,
            func.sum(RetargetingEvent.conversion_value).label('total_value'),
            func.count(RetargetingEvent.id).label('count')
        ).filter(
            RetargetingEvent.audience_id == audience_id,
            RetargetingEvent.conversion_value.isnot(None)
        ).group_by(
            RetargetingEvent.event_name
        ).order_by(
            func.sum(RetargetingEvent.conversion_value).desc()
        ).limit(10).all()

        return {
            "audience_id": audience_id,
            "name": audience.name,
            "platform": audience.platform,
            "total_size": audience.actual_size,
            "total_events": total_events,
            "events_by_type": events_by_type,
            "top_conversions": [
                {
                    "event_name": conv[0],
                    "total_value": float(conv[1]) if conv[1] else 0,
                    "count": conv[2]
                }
                for conv in top_conversions
            ]
        }

    def get_campaign_analytics(
        self,
        campaign_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Get analytics for a campaign"""

        campaign = db.query(RetargetingCampaign).filter(
            RetargetingCampaign.id == campaign_id
        ).first()

        if not campaign:
            raise Exception(f"Campaign {campaign_id} not found")

        # Get daily performance
        daily_performance = db.query(RetargetingPerformance).filter(
            RetargetingPerformance.campaign_id == campaign_id
        ).order_by(
            RetargetingPerformance.date.desc()
        ).limit(30).all()

        return {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "platform": campaign.platform,
            "total_impressions": campaign.impressions,
            "total_clicks": campaign.clicks,
            "total_conversions": campaign.conversions,
            "total_spend": campaign.spend,
            "total_revenue": campaign.revenue,
            "avg_ctr": campaign.ctr,
            "avg_cpc": campaign.cpc,
            "avg_cpa": campaign.cpa,
            "avg_roas": campaign.roas,
            "daily_performance": [
                {
                    "date": perf.date.isoformat(),
                    "impressions": perf.impressions,
                    "clicks": perf.clicks,
                    "conversions": perf.conversions,
                    "spend": perf.spend,
                    "revenue": perf.revenue,
                    "ctr": perf.ctr,
                    "roas": perf.roas
                }
                for perf in daily_performance
            ]
        }


# Singleton instance
retargeting_service = RetargetingService()
