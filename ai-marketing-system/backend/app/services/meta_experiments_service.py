"""
Meta (Facebook/Instagram) Experiments API Service

This service handles creating and managing A/B tests using Meta's Marketing API.
API Documentation: https://developers.facebook.com/docs/marketing-api/campaign-structure/campaign-experiments
"""

import httpx
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import hashlib
from scipy import stats
import numpy as np

from app.core.config import settings
from app.models.meta_ab_test import MetaABTest, MetaABTestVariant, MetaABTestResult
from app.models.user import User


class MetaExperimentsService:
    """Service for Meta (Facebook/Instagram) A/B testing experiments"""

    def __init__(self):
        self.access_token = settings.META_ACCESS_TOKEN
        self.app_id = settings.META_APP_ID
        self.app_secret = settings.META_APP_SECRET
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    async def verify_ad_account(self, ad_account_id: str) -> Dict:
        """Verify access to an ad account"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/act_{ad_account_id}",
                    params={
                        "access_token": self.access_token,
                        "fields": "id,name,currency,account_status,business_name,balance"
                    }
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "verified": True,
                    "account": {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "currency": data.get("currency"),
                        "status": data.get("account_status"),
                        "business_name": data.get("business_name"),
                        "balance": float(data.get("balance", 0)) / 100  # Convert from cents
                    }
                }

        except httpx.HTTPError as e:
            return {
                "verified": False,
                "error": f"Failed to verify ad account: {str(e)}"
            }

    async def create_experiment(
        self,
        db: Session,
        test: MetaABTest,
        variants: List[MetaABTestVariant]
    ) -> Dict:
        """Create a Facebook Experiment (A/B test)"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Step 1: Create Campaign if not exists
                if not test.campaign_id:
                    campaign = await self._create_campaign(client, test)
                    test.campaign_id = campaign["id"]

                # Step 2: Create Ad Sets for each variant
                ad_sets = []
                for variant in variants:
                    ad_set = await self._create_ad_set(client, test, variant)
                    variant.ad_set_id = ad_set["id"]
                    ad_sets.append(ad_set)

                # Step 3: Create Ads for each variant
                for variant, ad_set in zip(variants, ad_sets):
                    ad = await self._create_ad(client, test, variant, ad_set["id"])
                    variant.ad_id = ad["id"]

                # Step 4: Create the Experiment
                experiment_data = {
                    "name": test.name,
                    "description": test.description or "",
                    "type": "SPLIT_TEST",
                    "start_time": test.scheduled_start.isoformat() if test.scheduled_start else None,
                    "end_time": (test.scheduled_start + timedelta(days=test.duration_days)).isoformat() if test.scheduled_start else None,
                    "objective": self._get_objective_from_metric(test.success_metric),
                    "split_test_config": json.dumps({
                        "budget_split": self._calculate_budget_split(len(variants)),
                        "test_duration_days": test.duration_days
                    }),
                    "access_token": self.access_token
                }

                response = await client.post(
                    f"{self.base_url}/act_{test.ad_account_id}/experiments",
                    data=experiment_data
                )
                response.raise_for_status()
                experiment = response.json()

                test.meta_experiment_id = experiment.get("id")
                db.commit()

                return {
                    "success": True,
                    "experiment_id": experiment.get("id"),
                    "message": "Meta experiment created successfully"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create experiment: {str(e)}"
            }

    async def _create_campaign(self, client: httpx.AsyncClient, test: MetaABTest) -> Dict:
        """Create a Facebook campaign"""
        campaign_data = {
            "name": f"A/B Test: {test.name}",
            "objective": self._get_campaign_objective(test.test_type),
            "status": "PAUSED",  # Start paused
            "special_ad_categories": "[]",
            "access_token": self.access_token
        }

        response = await client.post(
            f"{self.base_url}/act_{test.ad_account_id}/campaigns",
            data=campaign_data
        )
        response.raise_for_status()
        return response.json()

    async def _create_ad_set(
        self,
        client: httpx.AsyncClient,
        test: MetaABTest,
        variant: MetaABTestVariant
    ) -> Dict:
        """Create a Facebook ad set"""
        targeting = variant.audience_override or test.target_audience

        ad_set_data = {
            "name": f"Variant: {variant.name}",
            "campaign_id": test.campaign_id,
            "daily_budget": int(variant.budget_override or test.budget_per_variant) * 100,  # Convert to cents
            "billing_event": "IMPRESSIONS",
            "optimization_goal": self._get_optimization_goal(test.success_metric),
            "targeting": json.dumps(targeting),
            "status": "PAUSED",
            "access_token": self.access_token
        }

        # Add placement if specified
        if variant.placement_override:
            ad_set_data["placement"] = json.dumps(variant.placement_override)

        response = await client.post(
            f"{self.base_url}/act_{test.ad_account_id}/adsets",
            data=ad_set_data
        )
        response.raise_for_status()
        return response.json()

    async def _create_ad(
        self,
        client: httpx.AsyncClient,
        test: MetaABTest,
        variant: MetaABTestVariant,
        ad_set_id: str
    ) -> Dict:
        """Create a Facebook ad"""
        # Create ad creative
        creative_data = {
            "name": f"Creative: {variant.name}",
            "object_story_spec": json.dumps({
                "page_id": await self._get_page_id(client),
                "link_data": {
                    "link": variant.link_url,
                    "message": variant.primary_text,
                    "name": variant.headline,
                    "description": variant.description_text,
                    "call_to_action": {
                        "type": variant.call_to_action or "LEARN_MORE"
                    }
                }
            })
        }

        # Add image or video if specified
        if variant.image_url:
            creative_data["image_url"] = variant.image_url
        elif variant.video_url:
            creative_data["video_id"] = await self._upload_video(client, variant.video_url)

        # Create creative
        creative_response = await client.post(
            f"{self.base_url}/act_{test.ad_account_id}/adcreatives",
            data={**creative_data, "access_token": self.access_token}
        )
        creative_response.raise_for_status()
        creative = creative_response.json()

        # Create ad
        ad_data = {
            "name": f"Ad: {variant.name}",
            "adset_id": ad_set_id,
            "creative": json.dumps({"creative_id": creative["id"]}),
            "status": "PAUSED",
            "access_token": self.access_token
        }

        response = await client.post(
            f"{self.base_url}/act_{test.ad_account_id}/ads",
            data=ad_data
        )
        response.raise_for_status()
        return response.json()

    async def start_experiment(self, db: Session, test_id: int) -> Dict:
        """Start a Meta experiment"""
        test = db.query(MetaABTest).filter(MetaABTest.id == test_id).first()
        if not test:
            return {"success": False, "error": "Test not found"}

        if not test.meta_experiment_id:
            return {"success": False, "error": "No Meta experiment ID found"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Update experiment status
                response = await client.post(
                    f"{self.base_url}/{test.meta_experiment_id}",
                    data={
                        "status": "ACTIVE",
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()

                # Update local status
                test.status = "running"
                test.started_at = datetime.utcnow()
                db.commit()

                return {
                    "success": True,
                    "message": "Experiment started successfully"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start experiment: {str(e)}"
            }

    async def pause_experiment(self, db: Session, test_id: int) -> Dict:
        """Pause a Meta experiment"""
        test = db.query(MetaABTest).filter(MetaABTest.id == test_id).first()
        if not test:
            return {"success": False, "error": "Test not found"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/{test.meta_experiment_id}",
                    data={
                        "status": "PAUSED",
                        "access_token": self.access_token
                    }
                )
                response.raise_for_status()

                test.status = "paused"
                db.commit()

                return {"success": True, "message": "Experiment paused"}

        except Exception as e:
            return {"success": False, "error": f"Failed to pause: {str(e)}"}

    async def fetch_experiment_results(
        self,
        db: Session,
        test_id: int
    ) -> Dict:
        """Fetch results from Meta for an experiment"""
        test = db.query(MetaABTest).filter(MetaABTest.id == test_id).first()
        if not test:
            return {"success": False, "error": "Test not found"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Fetch results for each variant
                variants = db.query(MetaABTestVariant).filter(
                    MetaABTestVariant.test_id == test_id
                ).all()

                for variant in variants:
                    if not variant.ad_id:
                        continue

                    # Fetch ad insights
                    response = await client.get(
                        f"{self.base_url}/{variant.ad_id}/insights",
                        params={
                            "access_token": self.access_token,
                            "fields": "impressions,reach,clicks,conversions,spend,cpm,cpc,ctr,conversion_rate",
                            "date_preset": "lifetime"
                        }
                    )
                    response.raise_for_status()
                    insights = response.json().get("data", [{}])[0]

                    # Update variant metrics
                    variant.impressions = insights.get("impressions", 0)
                    variant.reach = insights.get("reach", 0)
                    variant.clicks = insights.get("clicks", 0)
                    variant.conversions = insights.get("conversions", 0)
                    variant.spend = float(insights.get("spend", 0))
                    variant.cpm = float(insights.get("cpm", 0))
                    variant.cpc = float(insights.get("cpc", 0))
                    variant.ctr = float(insights.get("ctr", 0))
                    variant.conversion_rate = float(insights.get("conversion_rate", 0))

                    # Calculate ROAS if applicable
                    if variant.conversions > 0 and variant.spend > 0:
                        # This is simplified - in reality you'd need conversion value
                        variant.roas = (variant.conversions * 50) / variant.spend  # Assuming $50 value per conversion

                    # Store time-series data
                    await self._fetch_time_series_data(db, test, variant, client)

                db.commit()

                # Analyze results
                analysis = self.analyze_experiment(db, test_id)

                return {
                    "success": True,
                    "results": analysis
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to fetch results: {str(e)}"
            }

    async def _fetch_time_series_data(
        self,
        db: Session,
        test: MetaABTest,
        variant: MetaABTestVariant,
        client: httpx.AsyncClient
    ):
        """Fetch time-series data for a variant"""
        try:
            response = await client.get(
                f"{self.base_url}/{variant.ad_id}/insights",
                params={
                    "access_token": self.access_token,
                    "fields": "impressions,reach,clicks,conversions,spend,cpm,cpc,ctr",
                    "time_increment": "1",  # Daily data
                    "date_preset": "lifetime"
                }
            )
            response.raise_for_status()
            data = response.json().get("data", [])

            for day_data in data:
                # Create result record
                result = MetaABTestResult(
                    test_id=test.id,
                    variant_id=variant.id,
                    date=datetime.fromisoformat(day_data.get("date_start")),
                    impressions=day_data.get("impressions", 0),
                    reach=day_data.get("reach", 0),
                    clicks=day_data.get("clicks", 0),
                    conversions=day_data.get("conversions", 0),
                    spend=float(day_data.get("spend", 0)),
                    cpm=float(day_data.get("cpm", 0)),
                    cpc=float(day_data.get("cpc", 0)),
                    ctr=float(day_data.get("ctr", 0)),
                    conversion_rate=float(day_data.get("conversion_rate", 0))
                )
                db.add(result)

        except Exception as e:
            print(f"Error fetching time-series data: {e}")

    def analyze_experiment(self, db: Session, test_id: int) -> Dict:
        """Analyze experiment results and determine winner"""
        test = db.query(MetaABTest).filter(MetaABTest.id == test_id).first()
        if not test:
            return {}

        variants = db.query(MetaABTestVariant).filter(
            MetaABTestVariant.test_id == test_id
        ).all()

        if len(variants) < 2:
            return {"error": "Not enough variants to analyze"}

        # Get the success metric
        metric_field = self._get_metric_field(test.success_metric)

        # Calculate statistical significance
        variant_data = []
        for variant in variants:
            metric_value = getattr(variant, metric_field, 0)
            sample_size = variant.impressions if metric_field in ["ctr", "cpm"] else variant.clicks

            variant_data.append({
                "id": variant.id,
                "name": variant.name,
                "metric_value": metric_value,
                "sample_size": sample_size,
                "spend": variant.spend
            })

        # Sort by metric value
        variant_data.sort(key=lambda x: x["metric_value"], reverse=True)

        # Calculate confidence level using z-test for proportions
        if len(variant_data) >= 2 and variant_data[0]["sample_size"] > 30 and variant_data[1]["sample_size"] > 30:
            # Simplified statistical test
            p1 = variant_data[0]["metric_value"] / 100  # Convert percentage to proportion
            p2 = variant_data[1]["metric_value"] / 100
            n1 = variant_data[0]["sample_size"]
            n2 = variant_data[1]["sample_size"]

            if n1 > 0 and n2 > 0:
                # Pooled proportion
                p_pooled = (p1 * n1 + p2 * n2) / (n1 + n2)

                # Standard error
                se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))

                # Z-score
                if se > 0:
                    z = (p1 - p2) / se
                    # Two-tailed test
                    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
                    confidence_level = (1 - p_value) * 100
                else:
                    confidence_level = 0
            else:
                confidence_level = 0
        else:
            confidence_level = 0

        # Calculate improvement
        if variant_data[0]["metric_value"] > 0 and len(variant_data) > 1:
            improvement = ((variant_data[0]["metric_value"] - variant_data[1]["metric_value"]) /
                          variant_data[1]["metric_value"]) * 100
        else:
            improvement = 0

        # Determine winner
        winner_id = None
        if confidence_level >= 95 and improvement > 5:  # 95% confidence and >5% improvement
            winner_id = variant_data[0]["id"]

        return {
            "test_id": test_id,
            "total_impressions": sum(v.impressions for v in variants),
            "total_spend": sum(v.spend for v in variants),
            "winner_variant_id": winner_id,
            "winner_variant_name": variant_data[0]["name"] if variant_data else None,
            "confidence_level": confidence_level,
            "improvement_percentage": improvement,
            "variant_performance": variant_data,
            "statistical_significance": confidence_level >= 95,
            "recommendations": self._generate_recommendations(variant_data, confidence_level)
        }

    def _generate_recommendations(self, variant_data: List[Dict], confidence_level: float) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if confidence_level >= 95:
            recommendations.append("Results are statistically significant. Consider implementing the winning variant.")
        elif confidence_level >= 80:
            recommendations.append("Results show promise but need more data for statistical significance.")
        else:
            recommendations.append("Continue running the test to gather more data.")

        if len(variant_data) >= 2:
            if variant_data[0]["spend"] > variant_data[1]["spend"] * 1.5:
                recommendations.append("Consider balancing budget allocation between variants.")

        return recommendations

    def _get_campaign_objective(self, test_type: str) -> str:
        """Map test type to Facebook campaign objective"""
        mapping = {
            "ad_creative": "CONVERSIONS",
            "audience": "CONVERSIONS",
            "placement": "REACH",
            "budget": "CONVERSIONS",
            "bidding": "CONVERSIONS"
        }
        return mapping.get(test_type, "CONVERSIONS")

    def _get_optimization_goal(self, metric: str) -> str:
        """Map success metric to Facebook optimization goal"""
        mapping = {
            "ctr": "LINK_CLICKS",
            "conversions": "CONVERSIONS",
            "cpm": "IMPRESSIONS",
            "cpc": "LINK_CLICKS",
            "roas": "VALUE"
        }
        return mapping.get(metric, "LINK_CLICKS")

    def _get_objective_from_metric(self, metric: str) -> str:
        """Get experiment objective from success metric"""
        mapping = {
            "ctr": "LINK_CLICKS",
            "conversions": "CONVERSIONS",
            "cpm": "BRAND_AWARENESS",
            "cpc": "TRAFFIC",
            "roas": "CONVERSIONS"
        }
        return mapping.get(metric, "CONVERSIONS")

    def _get_metric_field(self, metric: str) -> str:
        """Get the database field name for a metric"""
        mapping = {
            "ctr": "ctr",
            "conversions": "conversions",
            "cpm": "cpm",
            "cpc": "cpc",
            "conversion_rate": "conversion_rate",
            "roas": "roas"
        }
        return mapping.get(metric, "ctr")

    def _calculate_budget_split(self, num_variants: int) -> List[float]:
        """Calculate even budget split for variants"""
        split = 100 / num_variants
        return [split] * num_variants

    async def _get_page_id(self, client: httpx.AsyncClient) -> str:
        """Get the first available Facebook Page ID"""
        response = await client.get(
            f"{self.base_url}/me/accounts",
            params={
                "access_token": self.access_token,
                "fields": "id"
            }
        )
        response.raise_for_status()
        pages = response.json().get("data", [])

        if not pages:
            raise Exception("No Facebook Pages found")

        return pages[0]["id"]

    async def _upload_video(self, client: httpx.AsyncClient, video_url: str) -> str:
        """Upload video to Facebook (placeholder - needs implementation)"""
        # This would need to handle video upload to Facebook
        # For now, return a placeholder
        return "placeholder_video_id"


# Singleton instance
meta_experiments_service = MetaExperimentsService()