"""
Facebook Lead Ads Integration Service

This service handles fetching leads from Facebook Lead Ads campaigns
and syncing them to the local leads database with consent tracking.

API Documentation: https://developers.facebook.com/docs/marketing-api/guides/lead-ads
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.lead import Lead, LeadSource


class FacebookLeadAdsService:
    """Service for Facebook Lead Ads integration"""

    def __init__(self):
        self.access_token = settings.META_ACCESS_TOKEN
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    async def verify_credentials(self) -> Dict:
        """Verify Facebook access token and permissions"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get token info
                response = await client.get(
                    f"{self.base_url}/me",
                    params={
                        "access_token": self.access_token,
                        "fields": "id,name"
                    }
                )
                response.raise_for_status()
                user_data = response.json()

                # Check for Lead Ads permissions
                permissions_response = await client.get(
                    f"{self.base_url}/me/permissions",
                    params={"access_token": self.access_token}
                )
                permissions_response.raise_for_status()
                permissions = permissions_response.json()

                # Check if we have leads_retrieval permission
                has_leads_permission = any(
                    p.get("permission") == "leads_retrieval" and p.get("status") == "granted"
                    for p in permissions.get("data", [])
                )

                return {
                    "verified": True,
                    "user_id": user_data.get("id"),
                    "user_name": user_data.get("name"),
                    "has_leads_permission": has_leads_permission,
                    "message": "Facebook credentials verified successfully" if has_leads_permission
                    else "Missing 'leads_retrieval' permission. Please grant Lead Ads access."
                }

        except httpx.HTTPError as e:
            return {
                "verified": False,
                "error": f"Failed to verify Facebook credentials: {str(e)}"
            }
        except Exception as e:
            return {
                "verified": False,
                "error": f"Unexpected error: {str(e)}"
            }

    async def get_lead_forms(self, page_id: str) -> List[Dict]:
        """Get all Lead Ad forms for a Facebook Page"""
        try:
            # First, get the page access token for this specific page
            page_token = None
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Get page access token
                    pages_response = await client.get(
                        f"{self.base_url}/me/accounts",
                        params={
                            "access_token": self.access_token,
                            "fields": "id,name,access_token"
                        }
                    )
                    pages_response.raise_for_status()
                    pages_data = pages_response.json()

                    # Find the specific page and get its token
                    for page in pages_data.get("data", []):
                        if page.get("id") == page_id:
                            page_token = page.get("access_token")
                            break

                    if not page_token:
                        print(f"Warning: No page token found for page {page_id}, using user token")
                        page_token = self.access_token

            except Exception as e:
                print(f"Error getting page token: {str(e)}, using user token")
                page_token = self.access_token

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Use the page access token for this request
                response = await client.get(
                    f"{self.base_url}/{page_id}/leadgen_forms",
                    params={
                        "access_token": page_token,  # Use page token instead of user token
                        "fields": "id,name,status,leads_count,created_time,questions"
                    }
                )

                # Log the response for debugging
                print(f"Lead forms response status: {response.status_code}")
                if response.status_code != 200:
                    print(f"Response content: {response.text}")

                response.raise_for_status()
                data = response.json()

                return data.get("data", [])

        except httpx.HTTPStatusError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to fetch lead forms: HTTP {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"Unexpected error in get_lead_forms: {str(e)}")
            raise Exception(f"Failed to fetch lead forms: {str(e)}")

    async def get_pages(self) -> List[Dict]:
        """Get all Facebook Pages the user manages"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/me/accounts",
                    params={
                        "access_token": self.access_token,
                        "fields": "id,name,access_token"
                    }
                )
                response.raise_for_status()
                data = response.json()

                return data.get("data", [])

        except Exception as e:
            raise Exception(f"Failed to fetch Facebook Pages: {str(e)}")

    async def get_leads_from_form(self, form_id: str, limit: int = 100) -> List[Dict]:
        """Get leads from a specific Lead Ad form"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    f"{self.base_url}/{form_id}/leads",
                    params={
                        "access_token": self.access_token,
                        "fields": "id,created_time,field_data",
                        "limit": limit
                    }
                )
                response.raise_for_status()
                data = response.json()

                return data.get("data", [])

        except Exception as e:
            raise Exception(f"Failed to fetch leads from form {form_id}: {str(e)}")

    async def sync_leads_to_database(
        self,
        form_id: str,
        db: Session,
        user_id: Optional[int] = None
    ) -> Dict:
        """Sync leads from Facebook Lead Ad form to local database"""
        try:
            # Fetch leads from Facebook
            fb_leads = await self.get_leads_from_form(form_id)

            if not fb_leads:
                return {
                    "success": True,
                    "imported": 0,
                    "skipped": 0,
                    "errors": [],
                    "message": "No leads found in this form"
                }

            imported = 0
            skipped = 0
            errors = []

            for fb_lead in fb_leads:
                try:
                    # Extract field data
                    field_data = {
                        item["name"]: item["values"][0]
                        for item in fb_lead.get("field_data", [])
                        if item.get("values")
                    }

                    # Get email (required)
                    email = field_data.get("email")
                    if not email:
                        errors.append(f"Lead {fb_lead.get('id')}: Missing email")
                        skipped += 1
                        continue

                    # Check if lead already exists
                    existing_lead = db.query(Lead).filter(Lead.email == email).first()
                    if existing_lead:
                        skipped += 1
                        continue

                    # Extract name fields
                    first_name = field_data.get("first_name", "")
                    last_name = field_data.get("last_name", "")
                    full_name = field_data.get("full_name", "")

                    # If no first/last name, try to split full_name
                    if not first_name and not last_name and full_name:
                        name_parts = full_name.split(" ", 1)
                        first_name = name_parts[0]
                        last_name = name_parts[1] if len(name_parts) > 1 else ""

                    # Create lead record
                    new_lead = Lead(
                        user_id=user_id,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        phone=field_data.get("phone_number", ""),
                        source=LeadSource.FACEBOOK,
                        email_consent=True,  # Facebook Lead Ads require user consent
                        consent_date=datetime.now(),
                        consent_source="facebook_lead_ads",
                        notes=f"Imported from Facebook Lead Ads. Form ID: {form_id}. FB Lead ID: {fb_lead.get('id')}"
                    )

                    db.add(new_lead)
                    imported += 1

                except Exception as e:
                    errors.append(f"Lead {fb_lead.get('id', 'unknown')}: {str(e)}")
                    skipped += 1
                    continue

            # Commit all leads
            db.commit()

            return {
                "success": True,
                "imported": imported,
                "skipped": skipped,
                "errors": errors,
                "message": f"Successfully imported {imported} leads from Facebook"
            }

        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to sync Facebook leads: {str(e)}")

    async def get_form_details(self, form_id: str) -> Dict:
        """Get detailed information about a Lead Ad form"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/{form_id}",
                    params={
                        "access_token": self.access_token,
                        "fields": "id,name,status,leads_count,created_time,questions,privacy_policy_url,follow_up_action_url"
                    }
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            raise Exception(f"Failed to fetch form details: {str(e)}")


# Singleton instance
facebook_lead_ads_service = FacebookLeadAdsService()
