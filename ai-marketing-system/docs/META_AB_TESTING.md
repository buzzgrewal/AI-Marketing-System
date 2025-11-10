# Meta (Facebook/Instagram) A/B Testing

## Overview
The AI Marketing System now includes comprehensive Meta A/B testing functionality that integrates with Facebook and Instagram's advertising platform. This feature allows you to test different ad variations to optimize campaign performance and maximize ROI.

## Features Implemented

### 🚀 Core Functionality
- **Multi-Platform Testing**: Test ads on Facebook, Instagram, or both simultaneously
- **Multiple Test Types**:
  - Ad Creative (images, videos, copy)
  - Audience targeting
  - Placement optimization
  - Budget allocation
  - Bidding strategies
- **Statistical Analysis**: Built-in confidence level calculations and winner determination
- **Real-time Results**: Fetch and analyze performance metrics from Meta's API
- **Budget Management**: Control daily spend per variant with automatic budget distribution

### 📊 Analytics & Reporting
- **Performance Metrics**:
  - Click-Through Rate (CTR)
  - Conversions
  - Cost Per Mille (CPM)
  - Cost Per Click (CPC)
  - Return on Ad Spend (ROAS)
- **Time-Series Analysis**: Track performance trends over time
- **Variant Comparison**: Side-by-side comparison with statistical significance
- **Automated Recommendations**: AI-powered insights based on test results

### 🎯 Test Management
- **Draft Mode**: Create and save tests before launching
- **Scheduling**: Schedule tests to start at optimal times
- **Pause/Resume**: Control test execution without losing data
- **Winner Declaration**: Manual or automatic winner selection based on statistical significance

## Technical Implementation

### Backend Architecture
```
backend/app/
├── models/
│   └── meta_ab_test.py          # Database models for Meta A/B tests
├── schemas/
│   └── meta_ab_test.py          # Pydantic schemas for validation
├── services/
│   └── meta_experiments_service.py  # Meta API integration service
└── api/routes/
    └── meta_ab_tests.py          # API endpoints
```

### Frontend Components
```
frontend/src/
├── pages/
│   └── MetaABTestPage.jsx       # Main UI for Meta A/B testing
└── services/
    └── api.js                    # API client with Meta A/B test endpoints
```

### Database Schema
- **meta_ab_tests**: Main test configuration and status
- **meta_ab_test_variants**: Individual test variants with creative content
- **meta_ab_test_results**: Time-series performance data

## Setup Requirements

### 1. Meta App Configuration
You need a Facebook App with the following:
- **App Type**: Business
- **Products**: Marketing API, Facebook Login
- **Permissions Required**:
  - `ads_management` - Create and manage ads
  - `ads_read` - Read ad performance data
  - `pages_manage_ads` - Manage page advertising
  - `business_management` - Access business assets

### 2. Environment Variables
Add these to your `backend/.env`:
```env
# Meta/Facebook Configuration
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
META_ACCESS_TOKEN=your_page_access_token_here
```

### 3. Ad Account Setup
- You need an active Facebook Ad Account
- The account must have a valid payment method
- Recommended: Start with a test ad account for development

## Using Meta A/B Testing

### Step 1: Access the Feature
Navigate to **Meta A/B Tests** in the sidebar menu.

### Step 2: Verify Ad Account
1. Click "Create Test"
2. Enter your Ad Account ID (found in Facebook Ads Manager)
3. Click "Verify" to confirm access

### Step 3: Configure Test
1. **Basic Settings**:
   - Test name and description
   - Platform selection (Facebook/Instagram/Both)
   - Test type (Creative, Audience, etc.)
   - Success metric (CTR, Conversions, etc.)
   - Budget per variant (daily spend)
   - Test duration (1-30 days)

2. **Create Variants** (2-5 variants):
   - Headline
   - Primary text (main ad copy)
   - Description
   - Call-to-action button
   - Destination URL
   - Creative assets (image/video URLs)

### Step 4: Launch Test
- Review configuration
- Click "Create Test" to save as draft
- Click "Start" button to launch the test
- Monitor real-time performance

### Step 5: Analyze Results
- View performance metrics for each variant
- Check statistical significance
- Review AI recommendations
- Declare winner when confidence level is sufficient

## API Endpoints

### Core Endpoints
- `GET /api/meta-ab-tests/` - List all tests
- `POST /api/meta-ab-tests/` - Create new test
- `GET /api/meta-ab-tests/{id}` - Get test details
- `PUT /api/meta-ab-tests/{id}` - Update test
- `DELETE /api/meta-ab-tests/{id}` - Delete test

### Test Control
- `POST /api/meta-ab-tests/{id}/start` - Start test
- `POST /api/meta-ab-tests/{id}/pause` - Pause test
- `POST /api/meta-ab-tests/{id}/refresh-results` - Fetch latest results
- `POST /api/meta-ab-tests/{id}/declare-winner` - Declare winner

### Analytics
- `GET /api/meta-ab-tests/stats` - Overall statistics
- `GET /api/meta-ab-tests/{id}/analysis` - Detailed test analysis
- `GET /api/meta-ab-tests/verify-account/{ad_account_id}` - Verify ad account

## Best Practices

### Test Design
1. **Clear Hypothesis**: Define what you're testing and why
2. **Single Variable**: Test one element at a time for clear results
3. **Sufficient Budget**: Allocate at least $50/day per variant
4. **Adequate Duration**: Run tests for at least 7 days
5. **Target Audience**: Use consistent audience across variants

### Statistical Significance
- **Confidence Level**: Wait for 95% confidence before declaring winner
- **Sample Size**: Ensure at least 1000 impressions per variant
- **Conversion Events**: Need 50+ conversions for reliable results

### Budget Management
- **Even Split**: Budget automatically splits evenly between variants
- **Daily Limits**: Set conservative daily limits to control spend
- **Monitor Closely**: Check spend daily during first 48 hours

## Troubleshooting

### Common Issues

#### 1. "Invalid Ad Account"
- **Cause**: No access to the specified ad account
- **Solution**: Ensure your access token has permissions for the account

#### 2. "Failed to Create Experiment"
- **Cause**: Missing required fields or invalid configuration
- **Solution**: Check all required fields are filled, verify budget meets minimum

#### 3. "No Results Available"
- **Cause**: Test just started or paused
- **Solution**: Wait 2-4 hours for initial data, ensure test is running

#### 4. "Token Expired"
- **Cause**: Access token has expired (60-day limit)
- **Solution**: Generate new long-lived token from Facebook

### Debug Checklist
1. ✅ Meta access token is valid
2. ✅ Ad account ID is correct (no 'act_' prefix)
3. ✅ Account has active payment method
4. ✅ Daily budget meets platform minimums ($1+ Facebook, $5+ Instagram)
5. ✅ Creative assets (images/videos) are accessible URLs
6. ✅ Target audience is properly defined

## Integration with Existing Features

### Lead Tracking
- Test-generated leads automatically sync to Leads module
- Source tracking shows which variant generated each lead
- Conversion tracking integrates with lead lifecycle

### Campaign Management
- A/B tests can be linked to existing campaigns
- Winner variants can update parent campaigns
- Performance data flows to campaign analytics

### Analytics Dashboard
- Meta test results appear in main analytics
- Combined reporting across email and social tests
- ROI calculations include Meta ad spend

## Limitations & Considerations

### Current Limitations
1. **Manual Creative Upload**: Images/videos must be hosted externally
2. **Basic Audience Targeting**: Advanced lookalike audiences not yet supported
3. **Single Objective**: Can't test multiple campaign objectives simultaneously
4. **No Automatic Scaling**: Winner must be manually scaled

### Cost Considerations
- **Ad Spend**: You pay Facebook directly for ad costs
- **API Limits**: Meta API has rate limits (200 calls/hour)
- **Minimum Budgets**: Platform minimums apply ($1-5/day)

### Privacy & Compliance
- All data collection follows Meta's privacy policies
- User consent required for retargeting pixels
- GDPR/CCPA compliance through Meta's tools

## Future Enhancements

### Planned Features
1. **Creative Asset Manager**: Upload and manage images/videos directly
2. **Advanced Audiences**: Lookalike and custom audience creation
3. **Multi-Objective Testing**: Test different campaign objectives
4. **Automatic Scaling**: Auto-apply winners to live campaigns
5. **Cross-Channel Testing**: Coordinate tests across Meta and Google
6. **Predictive Analytics**: ML-based test duration and budget recommendations
7. **Template Library**: Pre-built test templates for common scenarios
8. **Webhook Integration**: Real-time notifications for test events

### Roadmap
- **Q1 2025**: Creative asset management
- **Q2 2025**: Advanced audience features
- **Q3 2025**: Cross-channel orchestration
- **Q4 2025**: AI-powered optimization

## Security Notes

### Access Control
- Tests are user-specific (multi-tenant architecture)
- Ad account verification required before test creation
- Sensitive tokens stored encrypted

### API Security
- All Meta API calls use HTTPS
- Access tokens never exposed to frontend
- Rate limiting implemented to prevent abuse

## Support & Resources

### Meta Documentation
- [Facebook Marketing API](https://developers.facebook.com/docs/marketing-apis/)
- [Campaign Structure Guide](https://developers.facebook.com/docs/marketing-api/campaign-structure)
- [A/B Testing Best Practices](https://www.facebook.com/business/help/1738164643098669)

### Internal Documentation
- [META_API_SETUP.md](./META_API_SETUP.md) - Initial Meta API configuration
- [API Documentation](/api/docs) - Swagger/OpenAPI documentation

### Getting Help
1. Check error logs: `backend/logs/meta_ab_tests.log`
2. Verify token status: [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
3. Test API calls: [Graph API Explorer](https://developers.facebook.com/tools/explorer/)

## Summary

The Meta A/B Testing feature provides a complete solution for optimizing Facebook and Instagram advertising campaigns through systematic testing. With statistical analysis, real-time results, and AI-powered recommendations, marketers can make data-driven decisions to improve ad performance and ROI.

The implementation is production-ready but requires proper Meta API credentials and ad account access to function. Follow the setup guide carefully, start with small test budgets, and gradually scale based on results.