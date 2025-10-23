# API Examples

Common API usage examples for the AI Marketing Automation System.

## Authentication

### Register User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePassword123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePassword123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Leads Management

### Create Lead
```bash
curl -X POST "http://localhost:8000/api/leads/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cyclist@example.com",
    "first_name": "Alex",
    "last_name": "Rider",
    "sport_type": "cycling",
    "customer_type": "athlete",
    "email_consent": true,
    "consent_source": "website_signup"
  }'
```

### Get All Leads
```bash
curl -X GET "http://localhost:8000/api/leads/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Leads
```bash
curl -X GET "http://localhost:8000/api/leads/?search=Alex&email_consent=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Lead Statistics
```bash
curl -X GET "http://localhost:8000/api/leads/stats/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Content Generation

### Generate Social Media Post
```bash
curl -X POST "http://localhost:8000/api/content/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "social_post",
    "platform": "facebook",
    "topic": "New triathlon bike saddle launch",
    "tone": "enthusiastic",
    "target_audience": "triathletes",
    "additional_context": "Comfortable, aerodynamic, carbon fiber",
    "include_image": true
  }'
```

### Generate Email Template
```bash
curl -X POST "http://localhost:8000/api/content/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "email_template",
    "topic": "Spring Sale Announcement",
    "tone": "professional",
    "target_audience": "cyclists and triathletes",
    "additional_context": "20% off all products, limited time offer"
  }'
```

### Generate Ad Copy
```bash
curl -X POST "http://localhost:8000/api/content/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "ad_copy",
    "platform": "facebook",
    "topic": "Premier Bike Saddle",
    "tone": "enthusiastic",
    "target_audience": "competitive cyclists",
    "additional_context": "Lightweight carbon fiber, pressure relief design"
  }'
```

### Get All Content
```bash
curl -X GET "http://localhost:8000/api/content/?content_type=social_post&status=draft" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Approve Content
```bash
curl -X PUT "http://localhost:8000/api/content/123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

### Improve Content
```bash
curl -X POST "http://localhost:8000/api/content/improve/123?improvement_focus=engagement" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Campaigns

### Create Campaign
```bash
curl -X POST "http://localhost:8000/api/campaigns/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spring Sale 2024",
    "description": "Announcing our spring sale",
    "campaign_type": "email",
    "subject": "20% Off All Products This Weekend!",
    "content": "<h1>Spring Sale</h1><p>Get 20% off all cycling and triathlon products.</p>",
    "target_sport_type": "cycling"
  }'
```

### Send Campaign
```bash
curl -X POST "http://localhost:8000/api/campaigns/123/send" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Campaign Statistics
```bash
curl -X GET "http://localhost:8000/api/campaigns/123/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Campaign Overview
```bash
curl -X GET "http://localhost:8000/api/campaigns/stats/overview" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Python Examples

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    data={
        "username": "testuser",
        "password": "SecurePassword123"
    }
)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Generate content
content_response = requests.post(
    f"{BASE_URL}/api/content/generate",
    headers=headers,
    json={
        "content_type": "social_post",
        "platform": "instagram",
        "topic": "New bike saddle for long distance cycling",
        "tone": "enthusiastic",
        "target_audience": "endurance cyclists"
    }
)

content = content_response.json()
print(f"Generated content: {content['caption']}")

# Create lead
lead_response = requests.post(
    f"{BASE_URL}/api/leads/",
    headers=headers,
    json={
        "email": "newlead@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "sport_type": "triathlon",
        "email_consent": True,
        "consent_source": "website"
    }
)

lead = lead_response.json()
print(f"Created lead: {lead['id']}")
```

## JavaScript Examples

### Using Axios

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Login
const loginResponse = await axios.post(`${API_URL}/api/auth/login`,
  new URLSearchParams({
    username: 'testuser',
    password: 'SecurePassword123'
  })
);

const token = loginResponse.data.access_token;
const headers = { Authorization: `Bearer ${token}` };

// Generate content
const contentResponse = await axios.post(
  `${API_URL}/api/content/generate`,
  {
    content_type: 'social_post',
    platform: 'facebook',
    topic: 'Summer cycling tips',
    tone: 'friendly',
    target_audience: 'recreational cyclists'
  },
  { headers }
);

console.log('Generated:', contentResponse.data.caption);

// Get analytics
const statsResponse = await axios.get(
  `${API_URL}/api/leads/stats/overview`,
  { headers }
);

console.log('Stats:', statsResponse.data);
```

## Response Examples

### Successful Lead Creation
```json
{
  "id": 1,
  "email": "cyclist@example.com",
  "first_name": "Alex",
  "last_name": "Rider",
  "phone": null,
  "location": null,
  "email_consent": true,
  "sms_consent": false,
  "consent_date": "2024-01-15T10:30:00Z",
  "consent_source": "website_signup",
  "source": "manual",
  "status": "new",
  "sport_type": "cycling",
  "customer_type": "athlete",
  "engagement_score": 0,
  "last_contact_date": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### Generated Content Response
```json
{
  "id": 42,
  "content_type": "social_post",
  "platform": "facebook",
  "title": "Game-Changing Comfort",
  "caption": "Introducing our revolutionary new triathlon saddle! Designed with input from pro athletes, it delivers unmatched comfort during those long training rides. Perfect pressure relief channels and lightweight carbon construction. Your best ride awaits! 🚴‍♂️",
  "hashtags": "#triathlon #cycling #bikesaddle #comfort #performance #training",
  "image_url": null,
  "image_prompt": "Professional product photography of a sleek carbon fiber bike saddle, dramatic lighting, white background, close-up showing ergonomic design details",
  "status": "draft",
  "created_at": "2024-01-15T11:00:00Z"
}
```

### Campaign Statistics Response
```json
{
  "campaign": {
    "id": 5,
    "name": "Spring Sale 2024",
    "status": "completed"
  },
  "metrics": {
    "total_recipients": 1250,
    "total_sent": 1250,
    "total_delivered": 1235,
    "total_opened": 456,
    "total_clicked": 89,
    "total_converted": 23,
    "total_unsubscribed": 3,
    "open_rate": 36.9,
    "click_rate": 7.2,
    "conversion_rate": 1.9
  },
  "timeline": {
    "created_at": "2024-01-10T09:00:00Z",
    "scheduled_date": "2024-01-15T08:00:00Z",
    "sent_date": "2024-01-15T08:05:00Z"
  }
}
```

## Error Responses

### Authentication Error
```json
{
  "detail": "Could not validate credentials"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Resource Not Found
```json
{
  "detail": "Lead not found"
}
```

## Rate Limiting

The API implements rate limiting:
- Default: 60 requests per minute per user
- Exceeded: Returns 429 Too Many Requests

## Best Practices

1. **Store tokens securely** - Don't expose in client-side code
2. **Handle errors gracefully** - Check response status codes
3. **Use pagination** - For large datasets, use skip/limit parameters
4. **Cache responses** - When appropriate to reduce API calls
5. **Batch operations** - Import leads in bulk rather than one-by-one

## Testing

For interactive API testing, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
