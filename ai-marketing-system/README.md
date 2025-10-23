# AI Marketing Automation System

A comprehensive, compliant AI-powered marketing automation platform designed specifically for cycling, triathlon, and running businesses. This system helps you manage leads, generate engaging content, run email campaigns, and track performance—all while maintaining strict compliance with privacy laws and marketing regulations.

> **🚀 No Login Required!** This system runs without authentication for immediate use. Just start it up and begin using all features right away. Perfect for solo entrepreneurs and testing. See [NO_AUTH_MODE.md](NO_AUTH_MODE.md) for details.

## 🌟 Features

### Lead Management
- **Import & Organize**: Import leads from CSV/Excel with consent tracking
- **Advanced Segmentation**: Create complex segments with multiple conditions and AND/OR logic
- **Dynamic Segments**: Auto-updating segments that refresh as leads change
- **Compliance-First**: Built-in consent management (CAN-SPAM, GDPR, CCPA compliant)
- **Manual Entry**: Add individual leads with complete control over consent
- **Segment Preview**: Preview matching leads before saving segments

### AI Content Generation
- **Social Media Posts**: Generate engaging posts for Facebook, Instagram, Twitter, LinkedIn
- **Email Templates**: Create professional email marketing content
- **Ad Copy**: Generate compelling ad copy for paid advertising
- **Multiple Tones**: Professional, casual, friendly, or enthusiastic
- **Image Generation**: AI-powered image creation with DALL-E 3 and Stable Diffusion
- **Image Enhancement**: Improve existing images with AI
- **Content Improvement**: Enhance existing content for better engagement

### Email Campaigns
- **Targeted Campaigns**: Send to advanced segments or sport types
- **Custom Templates**: Build reusable email templates with variables
- **Template Variables**: Dynamic content with {{name}}, {{sport_type}}, etc.
- **Consent Verification**: Only sends to opted-in contacts
- **Performance Tracking**: Monitor opens, clicks, conversions
- **A/B Testing**: Test subject lines, content, templates, and sender names
- **Statistical Analysis**: Automatic winner selection based on performance
- **Background Processing**: Efficient bulk email sending

### Social Media Management
- **Multi-Platform Scheduling**: Schedule posts to Facebook, Instagram, Twitter, LinkedIn
- **Content Calendar**: Visual calendar view of scheduled posts
- **Best Time Suggestions**: AI-powered posting time recommendations
- **Draft Management**: Save and schedule posts for later
- **Bulk Scheduling**: Schedule multiple posts at once
- **Platform Status**: Monitor connection status for each platform
- **Engagement Tracking**: Track likes, comments, shares, and reach

### A/B Testing
- **Test Types**: Subject lines, content, templates, sender names
- **Multi-Variant**: Test 2-5 variants simultaneously
- **Sample Size Control**: Configure test percentage (1-100%)
- **Success Metrics**: Optimize for open rate, click rate, or conversion rate
- **Auto Winner Selection**: Automatically declare winner when statistically significant
- **Results Analysis**: Detailed performance comparison and insights

### Webhook Integration
- **Real-time Tracking**: Receive events from email providers automatically
- **Multi-Provider Support**: SendGrid, Mailchimp, Mailgun, and custom webhooks
- **Event Types**: Track opens, clicks, bounces, deliveries, unsubscribes
- **Automatic Updates**: Campaign and A/B test metrics update automatically
- **Security**: HMAC signature verification for webhook authenticity
- **Event Logs**: View and reprocess webhook events
- **Test Functionality**: Send test events to verify webhook configuration

### Analytics Dashboard
- **Real-time Metrics**: Track leads, campaigns, segments, and content performance
- **Visual Reports**: Charts and graphs for easy insights
- **Campaign Performance**: Open rates, click rates, conversion tracking
- **Content Analytics**: Engagement metrics for social media posts
- **A/B Test Results**: Statistical analysis and improvement tracking
- **Webhook Statistics**: Event processing and failure monitoring
- **AI-powered Insights**: Actionable recommendations

## 🛠 Technology Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **OpenRouter API**: AI content generation (Claude 3.5 Sonnet)
- **SQLite/PostgreSQL**: Database options
- **JWT Authentication**: Secure user authentication

### Frontend
- **React 18**: Modern UI library
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Data visualization
- **Axios**: HTTP client
- **React Router**: Client-side routing

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- OpenRouter API key ([Get one here](https://openrouter.ai))
- SMTP credentials (for email campaigns)

## 🚀 Installation & Setup

### 1. Clone or Navigate to Project

```bash
cd ai-marketing-system
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Important**: Configure these environment variables in `.env`:
- `SECRET_KEY`: Generate a secure random key
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `SMTP_*`: Your email service credentials

### 3. Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file (optional)
cp .env.example .env
```

### 4. Initialize Database

```bash
# From backend directory
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### 5. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```
Backend will run on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend will run on `http://localhost:3000`

## 📖 Usage Guide

### First Time Setup

1. **Open the System**
   - Navigate to `http://localhost:3000`
   - Dashboard loads immediately (no login required!)

2. **Import Your Leads**
   - Go to "Leads" section
   - Click "Import CSV"
   - **Important**: Only import contacts who have given explicit consent
   - Confirm consent checkbox before importing

3. **Create Segments** (Optional)
   - Go to "Segments" section
   - Click "New Segment"
   - Add conditions (sport_type, location, customer_type, etc.)
   - Choose AND/OR logic for multiple conditions
   - Preview matching leads
   - Save as dynamic (auto-updating) or static segment

4. **Build Email Templates** (Optional)
   - Go to "Email Templates"
   - Click "New Template"
   - Design your template with variables like {{name}}, {{sport_type}}
   - Add filters like {{name|capitalize}}
   - Preview with sample data
   - Save for reuse across campaigns

5. **Generate Content**
   - Go to "Content Generator"
   - Click "Generate Content"
   - Choose content type (social post, email, ad copy)
   - Fill in topic and details
   - Generate images with AI if needed
   - Review and approve generated content
   - Schedule directly to social media

6. **Create Campaign**
   - Go to "Campaigns"
   - Click "New Campaign"
   - Choose between custom content or template
   - Select target segment or sport type
   - Send to opted-in leads
   - Or create A/B test to optimize performance

7. **Set Up A/B Tests**
   - Go to "A/B Testing"
   - Click "New A/B Test"
   - Select campaign and test type
   - Create 2-5 variants
   - Set sample size and success metric
   - Let system auto-select winner or declare manually

8. **Configure Webhooks** (Optional)
   - Go to "Webhooks"
   - Click "New Webhook"
   - Select provider (SendGrid, Mailchimp, etc.)
   - Choose event type to track
   - Copy webhook URL
   - Configure in your email service provider
   - Receive real-time event tracking

9. **Track Performance**
   - View "Analytics" dashboard
   - Monitor campaign performance
   - Review A/B test results
   - Check webhook event logs
   - Review lead and segment statistics
   - Get AI-powered insights

### Advanced Feature Tips

**Email Templates:**
- Use variables for personalization: `{{name}}`, `{{sport_type}}`, `{{location}}`
- Apply filters: `{{name|capitalize}}`, `{{sport_type|upper}}`
- Set defaults: `{{first_name|default:"Athlete"}}`
- Categories: promotional, transactional, newsletter, announcement

**Segmentation:**
- Dynamic segments auto-update as leads change
- Static segments stay fixed (good for historical campaigns)
- Use AND logic for precise targeting, OR for broader reach
- Preview segments before using in campaigns
- Combine multiple conditions for advanced targeting

**A/B Testing:**
- Test one element at a time for clear insights
- Use at least 100 recipients per variant for statistical significance
- Let tests run for 24-48 hours before declaring winner
- Subject line tests typically show fastest results
- Auto-winner selection needs minimum 50 total recipients

**Social Media Scheduling:**
- Schedule posts during peak engagement times
- Use bulk scheduling for content calendar planning
- Draft posts for review before scheduling
- Schedule from AI-generated content with one click
- Track engagement metrics for each post

**Webhooks:**
- Configure webhooks for real-time tracking instead of manual updates
- Use signature verification for security
- Test webhooks before going live
- Monitor failed events and reprocess as needed
- Supported providers: SendGrid, Mailchimp, Mailgun

### CSV Import Format

Your CSV file should include these columns:

```csv
email,first_name,last_name,phone,location,sport_type,customer_type
john@example.com,John,Doe,555-0100,California,cycling,athlete
jane@example.com,Jane,Smith,555-0101,Texas,triathlon,coach
```

**Required:**
- `email`: Email address (required)

**Optional:**
- `first_name`: First name
- `last_name`: Last name
- `phone`: Phone number
- `location`: City/State
- `sport_type`: cycling, triathlon, running, multiple
- `customer_type`: athlete, coach, team, bike_fitter

## 🔐 Security & Compliance

### Data Protection
- Passwords hashed with bcrypt
- JWT tokens for authentication
- SQL injection protection via ORM
- CORS configuration for API security

### Marketing Compliance
- **Consent Tracking**: Every lead has consent status and date
- **Unsubscribe Links**: Automatic in all emails
- **CAN-SPAM Compliant**: Proper headers and opt-out
- **GDPR Ready**: Consent-first approach
- **No Automated Scraping**: Legal data sources only

### Email Best Practices
- Only sends to opted-in contacts
- Include company information
- Clear unsubscribe option
- Proper List-Unsubscribe headers

## 📊 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

**Authentication:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

**Leads:**
- `GET /api/leads/` - List all leads
- `POST /api/leads/` - Create lead
- `PUT /api/leads/{id}` - Update lead
- `POST /api/leads/import` - Import from CSV
- `GET /api/leads/stats/overview` - Lead statistics

**Segments:**
- `GET /api/segments/` - List all segments
- `POST /api/segments/` - Create segment
- `GET /api/segments/{id}/preview` - Preview segment leads
- `POST /api/segments/{id}/refresh` - Refresh segment count
- `GET /api/segments/fields/available` - Get available fields

**Content:**
- `POST /api/content/generate` - Generate AI content
- `GET /api/content/` - List content
- `PUT /api/content/{id}` - Update content
- `POST /api/content/improve/{id}` - Improve content

**Email Templates:**
- `GET /api/templates/` - List templates
- `POST /api/templates/` - Create template
- `POST /api/templates/render` - Preview template
- `GET /api/templates/variables/list` - Get available variables

**Campaigns:**
- `POST /api/campaigns/` - Create campaign
- `POST /api/campaigns/{id}/send` - Send campaign
- `GET /api/campaigns/{id}/stats` - Get campaign stats
- `GET /api/campaigns/stats/overview` - Overall stats

**A/B Testing:**
- `GET /api/ab-tests/` - List A/B tests
- `POST /api/ab-tests/` - Create A/B test
- `POST /api/ab-tests/{id}/start` - Start test
- `GET /api/ab-tests/{id}/results` - Get test results
- `POST /api/ab-tests/{id}/declare-winner` - Declare winner

**Social Media Scheduling:**
- `GET /api/schedule/` - List scheduled posts
- `POST /api/schedule/` - Schedule post
- `POST /api/schedule/from-content` - Schedule from generated content
- `GET /api/schedule/calendar` - Get calendar view
- `POST /api/schedule/{id}/post-now` - Post immediately

**Webhooks:**
- `GET /api/webhooks/` - List webhooks
- `POST /api/webhooks/` - Create webhook
- `GET /api/webhooks/{id}/events` - Get webhook events
- `POST /api/webhooks/{id}/test` - Send test event
- `GET /api/webhooks/providers` - List supported providers

## 💰 Cost Estimates

### Monthly Operating Costs

**AI Content Generation (OpenRouter):**
- Text Generation (Claude 3.5 Sonnet):
  - Light usage (50 generations/month): ~$5-10
  - Medium usage (200 generations/month): ~$20-30
  - Heavy usage (500+ generations/month): ~$50-100
- Image Generation (DALL-E 3 / Stable Diffusion):
  - Per image: ~$0.04-0.08
  - 50 images/month: ~$2-4
  - 200 images/month: ~$8-16

**Email Service (SMTP):**
- Gmail/Google Workspace: Free (up to 500/day)
- SendGrid Free Tier: 100 emails/day
- SendGrid Essentials: $19.95/month (up to 100k emails)
- Mailgun: $0.80 per 1,000 emails

**Webhook Integration:**
- SendGrid/Mailchimp/Mailgun: Free (included with email service)
- Real-time event tracking: No additional cost

**Social Media Platforms:**
- Facebook/Instagram/Twitter/LinkedIn API: Free
- Note: Currently using mock API - direct integration requires app approval

**Database & Hosting:**
- Local SQLite: Free
- Cloud hosting (optional): $5-50/month depending on provider

**Total Estimated Cost: $0-200/month**
(Depends on usage volume and chosen services)

**Cost-Saving Tips:**
- Start with free tiers to test
- Use image generation sparingly
- Batch email sends to reduce costs
- Monitor OpenRouter usage dashboard
- Consider PostgreSQL for production

## 🔧 Configuration

### Email SMTP Setup

**Gmail:**
1. Enable 2-factor authentication
2. Create an App Password
3. Use in SMTP_PASSWORD

**SendGrid:**
1. Create API key
2. SMTP_HOST=smtp.sendgrid.net
3. SMTP_PORT=587

### OpenRouter Models

Default models (can be changed in `.env`):
- Text: `anthropic/claude-3.5-sonnet`
- Image: `stability-ai/stable-diffusion-xl`

Available alternatives:
- `openai/gpt-4`
- `google/gemini-pro`
- `meta-llama/llama-2-70b-chat`

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Try different port
uvicorn main:app --port 8001
```

### Frontend build errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database errors
```bash
# Reset database
rm marketing_automation.db
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"
```

### Email not sending
- Verify SMTP credentials in `.env`
- Check firewall/antivirus blocking port 587
- Try with different SMTP provider

## 📝 Development

### Running Tests
```bash
cd backend
pytest
```

### Code Style
```bash
# Backend
black app/
flake8 app/

# Frontend
npm run lint
```

## 🤝 Support

For issues or questions:
1. Check this README
2. Review API documentation at `/docs`
3. Check environment variables
4. Verify all dependencies installed

## 📄 License

This project is proprietary software developed for marketing automation purposes.

## ⚠️ Important Notes

1. **Consent is Required**: Only contact individuals who have explicitly opted in
2. **Backup Your Data**: Regularly backup your database
3. **Keep Credentials Secure**: Never commit `.env` files
4. **Monitor Costs**: Track your OpenRouter API usage
5. **Test Before Sending**: Always test campaigns with small groups first

## 🎯 Roadmap

**Recently Completed:**
- [✅] Custom email templates builder
- [✅] Social media scheduling integration
- [✅] Advanced segmentation with dynamic filtering
- [✅] A/B testing for campaigns
- [✅] Webhook support for tracking

**Planned Enhancements:**
- [ ] SMS campaign support
- [ ] Multi-user accounts with team management
- [ ] Integration with Shopify API for e-commerce
- [ ] Integration with Meta Business Suite
- [ ] Direct social media API integration (Facebook, Twitter, LinkedIn)
- [ ] Advanced analytics with predictive insights
- [ ] Mobile app for on-the-go management
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Marketing automation workflows
- [ ] Lead scoring and qualification

---

**Built with compliance, powered by AI, focused on results.**
