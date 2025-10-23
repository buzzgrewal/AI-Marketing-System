# AI Marketing Automation System

A comprehensive, compliant AI-powered marketing automation platform designed specifically for cycling, triathlon, and running businesses. This system helps you manage leads, generate engaging content, run email campaigns, and track performance—all while maintaining strict compliance with privacy laws and marketing regulations.

> **🚀 No Login Required!** This system runs without authentication for immediate use. Just start it up and begin using all features right away. Perfect for solo entrepreneurs and testing. See [NO_AUTH_MODE.md](NO_AUTH_MODE.md) for details.

## 🌟 Features

### Lead Management
- **Import & Organize**: Import leads from CSV/Excel with consent tracking
- **Segmentation**: Filter by sport type, customer type, and consent status
- **Compliance-First**: Built-in consent management (CAN-SPAM, GDPR, CCPA compliant)
- **Manual Entry**: Add individual leads with complete control over consent

### AI Content Generation
- **Social Media Posts**: Generate engaging posts for Facebook, Instagram, Twitter, LinkedIn
- **Email Templates**: Create professional email marketing content
- **Ad Copy**: Generate compelling ad copy for paid advertising
- **Multiple Tones**: Professional, casual, friendly, or enthusiastic
- **Image Prompts**: AI-generated prompts for image creation
- **Content Improvement**: Enhance existing content for better engagement

### Email Campaigns
- **Targeted Campaigns**: Send to specific segments (sport type, status, etc.)
- **Consent Verification**: Only sends to opted-in contacts
- **Performance Tracking**: Monitor opens, clicks, conversions
- **Professional Templates**: Branded email templates included
- **Background Processing**: Efficient bulk email sending

### Analytics Dashboard
- **Real-time Metrics**: Track leads, campaigns, and content performance
- **Visual Reports**: Charts and graphs for easy insights
- **Campaign Performance**: Open rates, click rates, conversion tracking
- **Content Analytics**: Engagement metrics for social media posts
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

3. **Generate Content**
   - Go to "Content Generator"
   - Click "Generate Content"
   - Choose content type (social post, email, ad copy)
   - Fill in topic and details
   - Review and approve generated content

4. **Create Campaign**
   - Go to "Campaigns"
   - Click "New Campaign"
   - Set campaign name and email content
   - Choose target segment (optional)
   - Send to opted-in leads

5. **Track Performance**
   - View "Analytics" dashboard
   - Monitor campaign performance
   - Review lead statistics
   - Get AI-powered insights

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

**Content:**
- `POST /api/content/generate` - Generate AI content
- `GET /api/content/` - List content
- `PUT /api/content/{id}` - Update content
- `POST /api/content/improve/{id}` - Improve content

**Campaigns:**
- `POST /api/campaigns/` - Create campaign
- `POST /api/campaigns/{id}/send` - Send campaign
- `GET /api/campaigns/{id}/stats` - Get stats

## 💰 Cost Estimates

### Monthly Operating Costs

**AI Content Generation (OpenRouter):**
- Light usage (50 generations/month): ~$5-10
- Medium usage (200 generations/month): ~$20-30
- Heavy usage (500+ generations/month): ~$50-100

**Email Service (SMTP):**
- Gmail/Google Workspace: Free (up to 500/day)
- SendGrid Free Tier: 100 emails/day
- Mailgun: $0.80 per 1,000 emails

**Total Estimated Cost: $0-150/month**
(Depends on usage volume and chosen services)

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

Future enhancements:
- [ ] SMS campaign support
- [ ] Social media scheduling integration
- [ ] A/B testing for campaigns
- [ ] Advanced segmentation
- [ ] Webhook support for tracking
- [ ] Multi-user accounts
- [ ] Custom email templates builder
- [ ] Integration with Shopify API
- [ ] Integration with Meta Business Suite

---

**Built with compliance, powered by AI, focused on results.**
