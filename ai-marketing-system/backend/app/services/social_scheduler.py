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
        """Post to Facebook"""
        
        # Mock implementation - replace with actual Facebook Graph API
        # Real implementation would use settings.META_ACCESS_TOKEN
        
        try:
            # Simulate API call
            await asyncio.sleep(0.5)
            
            # Mock successful response
            mock_post_id = f"fb_{datetime.now().timestamp()}"
            mock_url = f"https://facebook.com/posts/{mock_post_id}"
            
            return {
                'success': True,
                'post_id': mock_post_id,
                'post_url': mock_url
            }
            
            # Real implementation would look like:
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(
            #         f"{self.platforms_config['facebook']['api_base']}/me/feed",
            #         params={'access_token': settings.META_ACCESS_TOKEN},
            #         json={
            #             'message': post.post_text,
            #             'link': post.image_url if post.image_url else None
            #         }
            #     )
            #     result = response.json()
            #     return {
            #         'success': True,
            #         'post_id': result.get('id'),
            #         'post_url': f"https://facebook.com/{result.get('id')}"
            #     }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _post_to_instagram(self, post: ScheduledPost) -> dict:
        """Post to Instagram"""
        
        # Instagram requires images, check if image_url is provided
        if not post.image_url:
            return {'success': False, 'error': 'Instagram posts require an image'}
        
        try:
            # Simulate API call
            await asyncio.sleep(0.5)
            
            mock_post_id = f"ig_{datetime.now().timestamp()}"
            mock_url = f"https://instagram.com/p/{mock_post_id}"
            
            return {
                'success': True,
                'post_id': mock_post_id,
                'post_url': mock_url
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
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
            # Mock implementation - in production, fetch real metrics from platform API
            await asyncio.sleep(0.3)
            
            # Mock metrics based on time since posting
            hours_since_post = (datetime.utcnow() - post.posted_at).total_seconds() / 3600
            
            post.likes_count = int(hours_since_post * 10)
            post.comments_count = int(hours_since_post * 2)
            post.shares_count = int(hours_since_post * 1)
            post.reach = int(hours_since_post * 50)
            
            if post.reach > 0:
                total_engagement = post.likes_count + post.comments_count + post.shares_count
                post.engagement_rate = int((total_engagement / post.reach) * 100)
            
            post.metrics_last_updated = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            print(f"Error updating metrics for post {post.id}: {str(e)}")
    
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

