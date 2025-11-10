# Meta (Facebook) API Setup & Requirements

## Overview
The AI Marketing System includes integration with Meta's (Facebook) Lead Ads API for importing leads from Facebook Lead Ad campaigns. This document outlines the requirements and setup process for making the Meta API fully functional.

## Current Implementation Status

### ✅ Implemented Features
1. **API Endpoints** (`/api/facebook-leads/`)
   - `/verify` - Verify Facebook credentials and permissions
   - `/pages` - Get Facebook Pages managed by the user
   - `/pages/{page_id}/forms` - Get Lead Ad forms for a specific page
   - `/forms/{form_id}` - Get detailed form information
   - `/forms/{form_id}/sync` - Sync leads from a form to the database
   - `/forms/{form_id}/preview` - Preview leads without saving

2. **Service Layer** (`app/services/facebook_lead_ads.py`)
   - Handles authentication with Facebook Graph API
   - Fetches pages, forms, and leads
   - Syncs leads to local database with consent tracking
   - Automatically tracks consent for GDPR/CCPA compliance

3. **Data Models & Schemas**
   - Pydantic schemas for request/response validation
   - Lead model with Facebook source tracking
   - Automatic consent tracking for imported leads

## Requirements for Full Functionality

### 1. Meta App Setup
You need to create a Meta App at [developers.facebook.com](https://developers.facebook.com/):

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app or use an existing one
3. Select "Business" as the app type
4. Add the "Facebook Login" and "Marketing API" products

### 2. Required Permissions
The app needs the following permissions:
- `leads_retrieval` - Required to fetch leads from Lead Ad forms
- `pages_manage_ads` - Required to access Lead Ad forms
- `pages_read_engagement` - Required to read page data
- `ads_management` - Required for full ad management features

### 3. Access Token
You need a **Page Access Token** (not a User Access Token):

1. Go to Graph API Explorer: https://developers.facebook.com/tools/explorer/
2. Select your app from the dropdown
3. Request the required permissions listed above
4. Generate a Page Access Token for the pages you want to manage
5. For production, convert to a long-lived token (60+ days)

### 4. Environment Variables
Add these to your `backend/.env` file:

```env
# Meta/Facebook Configuration
META_APP_ID=your-app-id-here
META_APP_SECRET=your-app-secret-here
META_ACCESS_TOKEN=your-page-access-token-here
META_PIXEL_ID=optional-pixel-id-for-tracking
```

### 5. Token Generation Steps

#### Step 1: Get User Access Token
```bash
https://www.facebook.com/v18.0/dialog/oauth?
  client_id={app-id}&
  redirect_uri={redirect-uri}&
  scope=leads_retrieval,pages_manage_ads,pages_read_engagement
```

#### Step 2: Exchange for Long-Lived User Token
```bash
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id={app-id}&
  client_secret={app-secret}&
  fb_exchange_token={short-lived-user-token}"
```

#### Step 3: Get Page Access Token
```bash
curl -X GET "https://graph.facebook.com/v18.0/{page-id}?
  fields=access_token&
  access_token={long-lived-user-token}"
```

## Testing the Integration

### 1. Verify Credentials
```bash
curl -X GET "http://localhost:8000/api/facebook-leads/verify"
```

Expected response:
```json
{
  "verified": true,
  "user_id": "123456789",
  "user_name": "Your Name",
  "has_leads_permission": true,
  "message": "Facebook credentials verified successfully"
}
```

### 2. Get Facebook Pages
```bash
curl -X GET "http://localhost:8000/api/facebook-leads/pages"
```

### 3. Get Lead Forms for a Page
```bash
curl -X GET "http://localhost:8000/api/facebook-leads/pages/{page_id}/forms"
```

### 4. Sync Leads from a Form
```bash
curl -X POST "http://localhost:8000/api/facebook-leads/forms/{form_id}/sync"
```

## Common Issues & Solutions

### Issue 1: "Missing 'leads_retrieval' permission"
**Solution:** Request the permission through App Review or use Test Mode with test users.

### Issue 2: "Invalid OAuth access token"
**Solution:** Regenerate the token and ensure it's a Page Access Token, not a User Token.

### Issue 3: "No lead forms found"
**Solution:**
- Ensure the page has active Lead Ad campaigns
- Verify the Page Access Token has the correct permissions
- Check if you're using the correct Page ID

### Issue 4: Rate Limiting
**Solution:** The API implements rate limiting. For production:
- Implement exponential backoff
- Cache responses where appropriate
- Use webhooks for real-time updates instead of polling

## Production Considerations

1. **Token Management**
   - Implement token refresh logic (tokens expire after 60 days)
   - Store tokens securely (encrypted in database)
   - Monitor token expiration and send alerts

2. **Webhooks (Recommended)**
   - Set up Lead Ads webhooks for real-time lead notifications
   - More efficient than polling
   - Reduces API calls and improves response time

3. **App Review**
   - For production use with non-test users, submit app for Facebook review
   - Required for `leads_retrieval` permission
   - Can take 5-10 business days

4. **Error Handling**
   - Implement retry logic for temporary failures
   - Log all API errors for debugging
   - Set up monitoring and alerting

5. **Data Privacy**
   - Always track consent properly (implemented)
   - Respect user opt-outs
   - Implement data retention policies
   - Ensure GDPR/CCPA compliance

## Testing Without Real Facebook Account

For development/testing without a real Facebook Lead Ads account:

1. Use Facebook's Test Users feature
2. Create test pages and test Lead Ad forms
3. Use the Graph API Explorer to generate test data
4. The service includes error handling that returns graceful messages when no data is available

## Frontend Integration

The Lead Sourcing page (`LeadSourcingPage.jsx`) includes:
- Facebook connection verification
- Page selection
- Form listing and preview
- Lead syncing with progress tracking
- Error handling and user feedback

## Current Limitations

1. **Token Expiration:** Tokens need manual refresh after 60 days
2. **No Webhook Support:** Currently uses polling instead of real-time webhooks
3. **Basic Field Mapping:** Only maps standard fields (email, name, phone)
4. **Single Token:** Uses one token for all operations (could use per-page tokens)

## Next Steps for Full Production Readiness

1. [ ] Implement token refresh automation
2. [ ] Add webhook support for real-time lead notifications
3. [ ] Implement custom field mapping
4. [ ] Add bulk operations for multiple forms
5. [ ] Implement lead deduplication logic
6. [ ] Add detailed logging and monitoring
7. [ ] Create admin UI for token management
8. [ ] Add support for Instagram Lead Ads
9. [ ] Implement lead quality scoring
10. [ ] Add automated follow-up sequences for new leads

## Resources

- [Meta Lead Ads API Documentation](https://developers.facebook.com/docs/marketing-api/guides/lead-ads)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
- [Meta Business Help Center](https://www.facebook.com/business/help/)

## Support

For issues with the Meta API integration:
1. Check the error logs in `backend/logs/`
2. Verify token permissions using the Access Token Debugger
3. Test with the Graph API Explorer
4. Review the Meta API changelog for breaking changes