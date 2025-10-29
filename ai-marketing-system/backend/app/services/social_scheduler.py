import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.scheduled_post import ScheduledPost
from app.models.content import GeneratedContent
from app.core.config import settings
import httpx


class SocialMediaScheduler:
    """Service for scheduling and posting to social media platforms"""

    def __init__(self):
        self.platforms_config = {
            'facebook': {
                'enabled': bool(settings.META_ACCESS_TOKEN),
                'api_base': 'https://graph.facebook.com/v18.0',
            },
            'instagram': {
                'enabled': bool(settings.META_ACCESS_TOKEN),
                'api_base': 'https://graph.facebook.com/v18.0',
            },
            'twitter': {
                'enabled': False,  # Would need Twitter API credentials
                'api_base': 'https://api.twitter.com/2',
            },
            'linkedin': {
                'enabled': False,  # Would need LinkedIn API credentials
                'api_base': 'https://api.linkedin.com/v2',
            }
        }

    async def verify_meta_token(self) -> dict:
        """Verify Meta access token and check permissions

        Returns:
            dict with status, permissions, page info, and Instagram account info
        """
        if not settings.META_ACCESS_TOKEN:
            return {
                'valid': False,
                'error': 'META_ACCESS_TOKEN not configured'
            }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Debug token to check permissions
                debug_response = await client.get(
                    f"{self.platforms_config['facebook']['api_base']}/debug_token",
                    params={
                        'input_token': settings.META_ACCESS_TOKEN,
                        'access_token': f"{settings.META_APP_ID}|{settings.META_APP_SECRET}"
                    }
                )

                if debug_response.status_code != 200:
                    return {
                        'valid': False,
                        'error': 'Failed to verify token'
                    }

                debug_data = debug_response.json().get('data', {})

                # Get page/account info
                me_response = await client.get(
                    f"{self.platforms_config['facebook']['api_base']}/me",
                    params={
                        'fields': 'id,name,instagram_business_account',
                        'access_token': settings.META_ACCESS_TOKEN
                    }
                )

                me_data = {}
                if me_response.status_code == 200:
                    me_data = me_response.json()

                return {
                    'valid': debug_data.get('is_valid', False),
                    'app_id': debug_data.get('app_id'),
                    'scopes': debug_data.get('scopes', []),
                    'expires_at': debug_data.get('expires_at'),
                    'page_id': me_data.get('id'),
                    'page_name': me_data.get('name'),
                    'instagram_account_id': me_data.get('instagram_business_account', {}).get('id'),
                    'instagram_enabled': bool(me_data.get('instagram_business_account'))
                }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    async def process_scheduled_posts(self, db: Session):
        """Process all posts that are scheduled for now or past"""
        
        current_time = datetime.utcnow()
        
        # Get posts that are due to be posted
        due_posts = db.query(ScheduledPost).filter(
            ScheduledPost.scheduled_time <= current_time,
            ScheduledPost.status == "scheduled",
            ScheduledPost.auto_post == True
        ).all()
        
        for post in due_posts:
            try:
                # Update status to posting
                post.status = "posting"
                db.commit()
                
                # Post to platform
                result = await self.post_to_platform(post, db)
                
                if result['success']:
                    post.status = "posted"
                    post.posted_at = datetime.utcnow()
                    post.platform_post_id = result.get('post_id')
                    post.platform_url = result.get('post_url')
                else:
                    post.status = "failed"
                    post.error_message = result.get('error')
                
                db.commit()
                
            except Exception as e:
                post.status = "failed"
                post.error_message = str(e)
                db.commit()
                print(f"Error posting scheduled post {post.id}: {str(e)}")
    
    async def post_to_platform(self, post: ScheduledPost, db: Session) -> dict:
        """Post content to the specified social media platform"""
        
        platform = post.platform.lower()
        
        # Check if platform is configured
        if not self.platforms_config.get(platform, {}).get('enabled'):
            return {
                'success': False,
                'error': f'{platform} integration not configured. Set up API credentials in settings.'
            }
        
        # Route to appropriate platform handler
        if platform == 'facebook':
            return await self._post_to_facebook(post)
        elif platform == 'instagram':
            return await self._post_to_instagram(post)
        elif platform == 'twitter':
            return await self._post_to_twitter(post)
        elif platform == 'linkedin':
            return await self._post_to_linkedin(post)
        else:
            return {'success': False, 'error': f'Unsupported platform: {platform}'}
    
    async def _post_to_facebook(self, post: ScheduledPost) -> dict:
        """Post to Facebook page using Graph API"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare post data
                post_data = {
                    'message': post.post_text,
                    'access_token': settings.META_ACCESS_TOKEN
                }

                # Add image/link if provided
                if post.image_url:
                    # If it's an image URL, use the 'link' parameter
                    # For photo posts, you'd use /photos endpoint instead
                    if post.image_url.startswith('http'):
                        post_data['link'] = post.image_url

                # Add custom platform settings if provided
                if post.platform_settings:
                    # Allow override of published status, targeting, etc.
                    post_data.update(post.platform_settings)

                # Post to Facebook page feed
                # Using /me/feed assumes the access token is a page access token
                # If you have a page ID, use /{page-id}/feed instead
                response = await client.post(
                    f"{self.platforms_config['facebook']['api_base']}/me/feed",
                    data=post_data
                )

                # Check for errors
                if response.status_code != 200:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    return {
                        'success': False,
                        'error': f'Facebook API error: {error_message}'
                    }

                result = response.json()
                post_id = result.get('id')

                # Construct the post URL
                # Format is typically: page_id_post_id
                post_url = f"https://www.facebook.com/{post_id}"

                return {
                    'success': True,
                    'post_id': post_id,
                    'post_url': post_url
                }

        except httpx.TimeoutException:
            return {'success': False, 'error': 'Facebook API request timed out'}
        except httpx.HTTPError as e:
            return {'success': False, 'error': f'HTTP error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    async def _post_to_instagram(self, post: ScheduledPost) -> dict:
        """Post to Instagram Business Account using Graph API

        Instagram posting requires a two-step process:
        1. Create a media container
        2. Publish the container

        Note: Requires an Instagram Business Account connected to a Facebook Page
        """

        # Instagram requires images
        if not post.image_url:
            return {'success': False, 'error': 'Instagram posts require an image'}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Step 1: Get Instagram Business Account ID
                # First, get the connected Instagram account from the page
                me_response = await client.get(
                    f"{self.platforms_config['instagram']['api_base']}/me",
                    params={
                        'fields': 'instagram_business_account',
                        'access_token': settings.META_ACCESS_TOKEN
                    }
                )

                if me_response.status_code != 200:
                    return {
                        'success': False,
                        'error': 'Failed to get Instagram Business Account. Ensure your Facebook Page is connected to an Instagram Business Account.'
                    }

                me_data = me_response.json()
                ig_account_id = me_data.get('instagram_business_account', {}).get('id')

                if not ig_account_id:
                    return {
                        'success': False,
                        'error': 'No Instagram Business Account found. Please connect your Instagram Business Account to your Facebook Page.'
                    }

                # Step 2: Create media container
                container_data = {
                    'image_url': post.image_url,
                    'caption': post.post_text,
                    'access_token': settings.META_ACCESS_TOKEN
                }

                # Add custom platform settings if provided
                if post.platform_settings:
                    container_data.update(post.platform_settings)

                container_response = await client.post(
                    f"{self.platforms_config['instagram']['api_base']}/{ig_account_id}/media",
                    data=container_data
                )

                if container_response.status_code != 200:
                    error_data = container_response.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    return {
                        'success': False,
                        'error': f'Instagram API error (create container): {error_message}'
                    }

                container_result = container_response.json()
                creation_id = container_result.get('id')

                # Step 3: Publish the media container
                publish_response = await client.post(
                    f"{self.platforms_config['instagram']['api_base']}/{ig_account_id}/media_publish",
                    data={
                        'creation_id': creation_id,
                        'access_token': settings.META_ACCESS_TOKEN
                    }
                )

                if publish_response.status_code != 200:
                    error_data = publish_response.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    return {
                        'success': False,
                        'error': f'Instagram API error (publish): {error_message}'
                    }

                publish_result = publish_response.json()
                media_id = publish_result.get('id')

                # Get the permalink for the post
                permalink_response = await client.get(
                    f"{self.platforms_config['instagram']['api_base']}/{media_id}",
                    params={
                        'fields': 'permalink',
                        'access_token': settings.META_ACCESS_TOKEN
                    }
                )

                post_url = f"https://www.instagram.com/p/{media_id}/"
                if permalink_response.status_code == 200:
                    permalink_data = permalink_response.json()
                    post_url = permalink_data.get('permalink', post_url)

                return {
                    'success': True,
                    'post_id': media_id,
                    'post_url': post_url
                }

        except httpx.TimeoutException:
            return {'success': False, 'error': 'Instagram API request timed out'}
        except httpx.HTTPError as e:
            return {'success': False, 'error': f'HTTP error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    async def _post_to_twitter(self, post: ScheduledPost) -> dict:
        """Post to Twitter"""
        
        try:
            # Simulate API call
            await asyncio.sleep(0.5)
            
            mock_post_id = f"tw_{datetime.now().timestamp()}"
            mock_url = f"https://twitter.com/status/{mock_post_id}"
            
            return {
                'success': True,
                'post_id': mock_post_id,
                'post_url': mock_url
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _post_to_linkedin(self, post: ScheduledPost) -> dict:
        """Post to LinkedIn"""
        
        try:
            # Simulate API call
            await asyncio.sleep(0.5)
            
            mock_post_id = f"li_{datetime.now().timestamp()}"
            mock_url = f"https://linkedin.com/feed/update/{mock_post_id}"
            
            return {
                'success': True,
                'post_id': mock_post_id,
                'post_url': mock_url
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def update_post_metrics(self, post: ScheduledPost, db: Session):
        """Fetch and update engagement metrics for a posted item"""

        if post.status != "posted" or not post.platform_post_id:
            return

        platform = post.platform.lower()

        try:
            if platform == 'facebook':
                await self._update_facebook_metrics(post)
            elif platform == 'instagram':
                await self._update_instagram_metrics(post)
            # Twitter and LinkedIn would be handled similarly

            post.metrics_last_updated = datetime.utcnow()
            db.commit()

        except Exception as e:
            print(f"Error updating metrics for post {post.id}: {str(e)}")

    async def _update_facebook_metrics(self, post: ScheduledPost):
        """Fetch Facebook post metrics using Graph API"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch post insights
                response = await client.get(
                    f"{self.platforms_config['facebook']['api_base']}/{post.platform_post_id}",
                    params={
                        'fields': 'likes.summary(true),comments.summary(true),shares,reactions.summary(true)',
                        'access_token': settings.META_ACCESS_TOKEN
                    }
                )

                if response.status_code != 200:
                    print(f"Failed to fetch Facebook metrics for post {post.platform_post_id}")
                    return

                data = response.json()

                # Update metrics
                post.likes_count = data.get('likes', {}).get('summary', {}).get('total_count', 0)
                post.comments_count = data.get('comments', {}).get('summary', {}).get('total_count', 0)
                post.shares_count = data.get('shares', {}).get('count', 0)

                # Try to get insights for reach (requires additional permissions)
                insights_response = await client.get(
                    f"{self.platforms_config['facebook']['api_base']}/{post.platform_post_id}/insights",
                    params={
                        'metric': 'post_impressions,post_engaged_users',
                        'access_token': settings.META_ACCESS_TOKEN
                    }
                )

                if insights_response.status_code == 200:
                    insights_data = insights_response.json()
                    for metric in insights_data.get('data', []):
                        if metric.get('name') == 'post_impressions':
                            post.reach = metric.get('values', [{}])[0].get('value', 0)
                        elif metric.get('name') == 'post_engaged_users':
                            engaged = metric.get('values', [{}])[0].get('value', 0)
                            if post.reach > 0:
                                post.engagement_rate = int((engaged / post.reach) * 100)

        except Exception as e:
            print(f"Error fetching Facebook metrics: {str(e)}")

    async def _update_instagram_metrics(self, post: ScheduledPost):
        """Fetch Instagram post metrics using Graph API"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch media insights
                response = await client.get(
                    f"{self.platforms_config['instagram']['api_base']}/{post.platform_post_id}",
                    params={
                        'fields': 'like_count,comments_count,insights.metric(engagement,impressions,reach,saved)',
                        'access_token': settings.META_ACCESS_TOKEN
                    }
                )

                if response.status_code != 200:
                    print(f"Failed to fetch Instagram metrics for post {post.platform_post_id}")
                    return

                data = response.json()

                # Update basic metrics
                post.likes_count = data.get('like_count', 0)
                post.comments_count = data.get('comments_count', 0)

                # Process insights
                insights = data.get('insights', {}).get('data', [])
                for insight in insights:
                    name = insight.get('name')
                    values = insight.get('values', [{}])[0].get('value', 0)

                    if name == 'impressions':
                        post.reach = values
                    elif name == 'reach':
                        # Use reach if available (more accurate than impressions)
                        post.reach = values
                    elif name == 'engagement':
                        if post.reach > 0:
                            post.engagement_rate = int((values / post.reach) * 100)
                    elif name == 'saved':
                        post.shares_count = values  # Treating 'saved' as shares

        except Exception as e:
            print(f"Error fetching Instagram metrics: {str(e)}")
    
    def get_next_posting_time(self, post: ScheduledPost) -> Optional[datetime]:
        """Calculate when the post will be processed"""
        
        if post.status != "scheduled":
            return None
        
        return post.scheduled_time
    
    def validate_post_content(self, platform: str, post_text: str, image_url: Optional[str] = None) -> dict:
        """Validate post content for platform requirements"""
        
        errors = []
        warnings = []
        
        platform = platform.lower()
        
        # Platform-specific validation
        if platform == 'twitter':
            if len(post_text) > 280:
                errors.append(f"Twitter posts must be 280 characters or less (current: {len(post_text)})")
        
        elif platform == 'instagram':
            if not image_url:
                errors.append("Instagram posts require an image")
            if len(post_text) > 2200:
                warnings.append(f"Instagram captions over 2200 characters may be truncated")
        
        elif platform == 'facebook':
            if len(post_text) > 63206:
                errors.append("Facebook posts must be under 63,206 characters")
        
        elif platform == 'linkedin':
            if len(post_text) > 3000:
                errors.append("LinkedIn posts must be 3000 characters or less")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Singleton instance
social_scheduler = SocialMediaScheduler()

