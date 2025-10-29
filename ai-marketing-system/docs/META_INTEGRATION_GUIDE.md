# Meta/Facebook Integration Guide

This guide explains how to use the Meta/Facebook integration to post to Facebook and Instagram, track engagement metrics, and monitor website visitors with Meta Pixel.

## Overview

The Meta integration enables:
- ✅ **Facebook Page Posts** - Automatically post content to your Facebook Page
- ✅ **Instagram Business Posts** - Post images with captions to Instagram
- ✅ **Engagement Metrics** - Track likes, comments, shares, and reach
- ✅ **Meta Pixel Tracking** - Monitor website visitor behavior (optional)

## Prerequisites

1. **Facebook Page** - You need a Facebook Page (not a personal profile)
2. **Instagram Business Account** (for Instagram posting) - Must be connected to your Facebook Page
3. **Meta App** - Create an app in Meta for Developers
4. **Page Access Token** - Long-lived access token with proper permissions

## Setup Instructions

### Step 1: Create a Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. Choose **Business** as the app type
4. Fill in app details:
   - **App Name**: Your app name (e.g., "My Marketing Automation")
   - **Contact Email**: Your email
5. Click **Create App**
6. Note your **App ID** and **App Secret** (Settings → Basic)

### Step 2: Get a Page Access Token

#### Option A: Using Graph API Explorer (Recommended for Testing)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **Generate Access Token**
4. Select your Facebook Page
5. Grant required permissions:
   - `pages_manage_posts` - To create posts
   - `pages_read_engagement` - To read post metrics
   - `instagram_basic` - For Instagram posting
   - `instagram_content_publish` - To publish Instagram content
6. Copy the **User Access Token**
7. Convert it to a **Long-Lived Token**:
   ```bash
   curl -i -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
   ```
8. Convert the Long-Lived User Token to a **Page Access Token**:
   ```bash
   curl -i -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=LONG_LIVED_USER_TOKEN"
   ```
9. Copy the `access_token` for your page (this is your Page Access Token)

#### Option B: Using Facebook Business Settings (For Production)

1. Go to [Facebook Business Settings](https://business.facebook.com/settings/)
2. Navigate to **Users** → **System Users**
3. Create a system user
4. Assign assets (your Facebook Page) to the system user
5. Generate a token with required permissions
6. This token will be long-lived and suitable for production

### Step 3: Configure Backend (.env)

Add your credentials to `backend/.env`:

```bash
# Meta/Facebook Configuration
META_APP_ID=1145155901127075
META_APP_SECRET=7150f697cdab8685c34c00ed1897aea4
META_ACCESS_TOKEN=YOUR_PAGE_ACCESS_TOKEN_HERE
META_PIXEL_ID=  # Optional: For tracking (see Step 5)
```

### Step 4: Connect Instagram Business Account (For Instagram Posting)

1. Go to your Facebook Page
2. Click **Settings** → **Instagram**
3. Click **Connect Account** and log in to your Instagram Business account
4. Ensure your Instagram account is a **Business Account** (not Creator or Personal)

To verify the connection:
```bash
curl -X GET "https://graph.facebook.com/v18.0/me?fields=instagram_business_account&access_token=YOUR_PAGE_ACCESS_TOKEN"
```

### Step 5: Set Up Meta Pixel (Optional - For Tracking)

If you want to track website visitors:

1. Go to [Meta Business Manager](https://business.facebook.com/)
2. Navigate to **Events Manager**
3. Click **Connect Data Sources** → **Web** → **Meta Pixel**
4. Name your pixel and click **Create**
5. Copy the **Pixel ID** (16-digit number)
6. Add to `backend/.env`:
   ```bash
   META_PIXEL_ID=1234567890123456
   ```
7. Add to `frontend/.env`:
   ```bash
   VITE_META_PIXEL_ID=1234567890123456
   ```

The Meta Pixel code is already installed in `frontend/index.html` and will automatically activate when you set the Pixel ID.

## Verify Your Setup

### Test Backend Configuration

1. Start your backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Open your browser and go to:
   ```
   http://localhost:8000/api/social-scheduling/meta/verify
   ```

3. You should see a response like:
   ```json
   {
     "status": "success",
     "message": "Meta integration is properly configured",
     "details": {
       "app_id": "1145155901127075",
       "page_id": "123456789",
       "page_name": "Your Page Name",
       "instagram_enabled": true,
       "instagram_account_id": "987654321",
       "scopes": ["pages_manage_posts", "pages_read_engagement", "instagram_basic", "instagram_content_publish"],
       "expires_at": 0
     }
   }
   ```

### Common Issues

**Error: "Meta token verification failed"**
- Check that `META_ACCESS_TOKEN` is a Page Access Token (not User Token)
- Verify the token hasn't expired
- Ensure required permissions are granted

**Error: "No Instagram Business Account found"**
- Connect your Instagram Business Account to your Facebook Page
- Ensure it's a Business account, not Creator or Personal
- Wait a few minutes after connecting and try again

**Error: "Instagram API error (create container): Invalid image URL"**
- Ensure the image URL is publicly accessible
- Use HTTPS URLs only
- Check the image format (JPEG or PNG recommended)

## Usage Examples

### 1. Schedule a Facebook Post

```python
import requests

response = requests.post("http://localhost:8000/api/social-scheduling/", json={
    "platform": "facebook",
    "post_text": "Check out our new cycling gear! 🚴‍♂️",
    "image_url": "https://example.com/image.jpg",
    "scheduled_time": "2025-10-30T10:00:00Z",
    "auto_post": True
})

print(response.json())
```

### 2. Schedule an Instagram Post

```python
import requests

response = requests.post("http://localhost:8000/api/social-scheduling/", json={
    "platform": "instagram",
    "post_text": "Beautiful sunset ride! 🌅 #cycling #nature",
    "image_url": "https://example.com/sunset.jpg",  # Required for Instagram
    "scheduled_time": "2025-10-30T18:00:00Z",
    "auto_post": True
})

print(response.json())
```

### 3. Post Immediately

```python
import requests

# Create the scheduled post
response = requests.post("http://localhost:8000/api/social-scheduling/", json={
    "platform": "facebook",
    "post_text": "Breaking news! 🎉",
    "scheduled_time": "2025-10-30T09:00:00Z",
    "auto_post": False
})

post_id = response.json()["id"]

# Post it immediately
post_now = requests.post(f"http://localhost:8000/api/social-scheduling/{post_id}/post-now")
print(post_now.json())
```

### 4. Fetch Post Metrics

```python
import requests

# Refresh metrics for a posted item
response = requests.post(f"http://localhost:8000/api/social-scheduling/{post_id}/metrics/refresh")

# Get updated post details
post = requests.get(f"http://localhost:8000/api/social-scheduling/{post_id}")
metrics = post.json()

print(f"Likes: {metrics['likes_count']}")
print(f"Comments: {metrics['comments_count']}")
print(f"Shares: {metrics['shares_count']}")
print(f"Reach: {metrics['reach']}")
print(f"Engagement Rate: {metrics['engagement_rate']}%")
```

### 5. Using the Web Interface

1. Go to the **Social Scheduling** page in your web app
2. Click **Create New Post**
3. Select platform (Facebook or Instagram)
4. Enter your content
5. Upload or provide image URL (required for Instagram)
6. Choose scheduling time
7. Toggle **Auto Post** to automatically publish at scheduled time
8. Click **Schedule Post**

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/social-scheduling/` | POST | Create a scheduled post |
| `/api/social-scheduling/from-content` | POST | Schedule from AI-generated content |
| `/api/social-scheduling/bulk` | POST | Schedule multiple posts at once |
| `/api/social-scheduling/` | GET | List all scheduled posts |
| `/api/social-scheduling/{id}` | GET | Get specific post details |
| `/api/social-scheduling/{id}/post-now` | POST | Post immediately |
| `/api/social-scheduling/{id}/metrics/refresh` | POST | Refresh engagement metrics |
| `/api/social-scheduling/platforms/status` | GET | Check platform integration status |
| `/api/social-scheduling/meta/verify` | GET | Verify Meta credentials |

## Platform-Specific Requirements

### Facebook
- **Max length**: 63,206 characters
- **Image**: Optional (but recommended)
- **Supported media**: Images, links, text
- **Best practices**:
  - Keep posts under 400 characters for better engagement
  - Use high-quality images (1200x630 px recommended)
  - Include a call-to-action

### Instagram
- **Max caption length**: 2,200 characters
- **Image**: **Required**
- **Supported formats**: JPEG, PNG
- **Image requirements**:
  - Must be publicly accessible HTTPS URL
  - Minimum 320px wide
  - Aspect ratio between 4:5 and 1.91:1
- **Best practices**:
  - Use square images (1080x1080 px) for best results
  - Include relevant hashtags (up to 30)
  - First 125 characters appear in feed - make them count

## Required Permissions

Your Page Access Token must have these permissions:

### For Facebook Posting
- `pages_manage_posts` - Create and publish posts
- `pages_read_engagement` - Read post metrics

### For Instagram Posting
- `instagram_basic` - Access Instagram account info
- `instagram_content_publish` - Publish content to Instagram

### For Advanced Metrics
- `read_insights` - Access detailed insights (optional)

## Troubleshooting

### Token Expires
Page Access Tokens can expire. To get a non-expiring token:
1. Follow Step 2, Option B (System Users)
2. System User tokens don't expire unless revoked

### Rate Limits
- Facebook: 200 calls per hour per user
- Instagram: 30 posts per day per account

If you hit rate limits, the API will return an error. The system will retry failed posts.

### Permissions Denied
If you see permission errors:
1. Re-generate your access token
2. Ensure all required permissions are checked
3. Verify you're using a Page Access Token (not User Token)

### Instagram Container Creation Fails
Common causes:
- Image URL is not publicly accessible
- Image format is unsupported
- Image doesn't meet size requirements
- Account is not a Business account

## Security Best Practices

1. **Never commit tokens** - Keep `.env` files out of version control
2. **Use environment variables** - Never hardcode credentials
3. **Rotate tokens regularly** - Generate new tokens every 60 days
4. **Monitor access** - Check your app's usage in Meta Business Manager
5. **Limit permissions** - Only request permissions you actually need

## Support

If you need help:
1. Check the [Meta for Developers Documentation](https://developers.facebook.com/docs/)
2. Use the Graph API Explorer to test endpoints
3. Check the error logs in `backend/logs/`
4. Visit the [Facebook Platform Status](https://developers.facebook.com/status/) page

## Additional Resources

- [Meta Graph API Reference](https://developers.facebook.com/docs/graph-api/)
- [Facebook Page API](https://developers.facebook.com/docs/pages-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/)
- [Meta Pixel Documentation](https://developers.facebook.com/docs/meta-pixel/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
