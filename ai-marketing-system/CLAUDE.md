# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Marketing Automation System designed for cycling, triathlon, and running businesses. It's a full-stack web application that enables businesses to manage leads, generate marketing content using AI, run email campaigns, and track performance—all while maintaining strict compliance with privacy laws (CAN-SPAM, GDPR, CCPA).

**Tech Stack:**
- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Frontend**: React 18 with Vite, Tailwind CSS, and Recharts
- **AI**: OpenRouter API (Claude 3.5 Sonnet for content generation)
- **Database**: SQLite (dev), PostgreSQL (production)

## Development Commands

### Backend (FastAPI)

**Location**: `backend/`

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server (with auto-reload)
python main.py
# Runs on http://localhost:8000
# API docs at http://localhost:8000/docs

# Run with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run production server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# Database migrations (if using Alembic)
alembic revision --autogenerate -m "migration message"
alembic upgrade head

# Run tests
pytest
pytest -v  # verbose
pytest tests/test_specific.py  # single test file
```

### Frontend (React + Vite)

**Location**: `frontend/`

```bash
# Install dependencies
npm install

# Run development server (with hot reload)
npm run dev
# Runs on http://localhost:3000

# Build for production
npm run build
# Output: frontend/dist/

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Environment Setup

Copy `.env.example` to `backend/.env` and configure:
```bash
cp .env.example backend/.env
```

Required environment variables:
- `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
- `OPENROUTER_API_KEY`: OpenRouter API key from https://openrouter.ai
- `SMTP_*`: Email configuration for campaigns (Gmail, SendGrid, etc.)

## Architecture & Code Organization

### Backend Architecture (FastAPI)

The backend follows a **layered architecture** with clear separation of concerns:

```
backend/
├── main.py                    # FastAPI app initialization, CORS, router registration
├── app/
│   ├── api/routes/           # API endpoint definitions
│   │   ├── auth.py          # User registration, login, JWT tokens
│   │   ├── leads.py         # Lead CRUD, import, consent tracking
│   │   ├── campaigns.py     # Campaign creation, sending, tracking
│   │   └── content.py       # AI content generation endpoints
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings (loaded from .env via Pydantic)
│   │   └── security.py      # Password hashing, JWT token handling
│   ├── models/              # SQLAlchemy ORM models (database schema)
│   │   ├── user.py          # User model with password hashing
│   │   ├── lead.py          # Lead/contact model with consent tracking
│   │   ├── campaign.py      # Campaign model with performance metrics
│   │   └── content.py       # Generated content storage
│   ├── schemas/             # Pydantic schemas (request/response validation)
│   │   ├── user.py          # UserCreate, UserResponse, Token
│   │   ├── lead.py          # LeadCreate, LeadUpdate, LeadResponse
│   │   ├── campaign.py      # CampaignCreate, CampaignResponse
│   │   └── content.py       # ContentRequest, ContentResponse
│   ├── services/            # Business logic layer
│   │   ├── ai_content_generator.py  # OpenRouter API integration
│   │   └── email_service.py         # SMTP email sending
│   └── db/                  # Database configuration
│       ├── session.py       # SQLAlchemy session/engine setup
│       └── base.py          # Base model for all ORM models
```

**Key Design Patterns:**

1. **Dependency Injection**: Database sessions injected via `get_db()` dependency
2. **Current User Pattern**: `get_current_user()` dependency extracts user from JWT token
3. **Service Layer**: Business logic isolated in `services/` (AI generation, email sending)
4. **Schema Validation**: Pydantic schemas validate all inputs/outputs automatically
5. **ORM Models**: SQLAlchemy models handle all database operations

**Database Relationships:**
- `User` → `Lead` (one-to-many): Each lead belongs to a user
- `User` → `Campaign` (one-to-many): Each campaign belongs to a user
- `User` → `Content` (one-to-many): Each content piece belongs to a user
- `Campaign` → `Lead` (many-to-many): Campaigns can target multiple leads

### Frontend Architecture (React)

The frontend uses **component-based architecture** with React Router for routing:

```
frontend/src/
├── main.jsx              # App entry point, React Router setup
├── App.jsx              # Root component with route definitions
├── components/
│   └── common/          # Reusable UI components
│       ├── Layout.jsx   # Page wrapper with sidebar and navbar
│       ├── Navbar.jsx   # Top navigation bar
│       └── Sidebar.jsx  # Left sidebar navigation
├── pages/               # Full-page components (one per route)
│   ├── LoginPage.jsx           # Authentication
│   ├── RegisterPage.jsx        # User signup
│   ├── DashboardPage.jsx       # Home page with stats
│   ├── LeadsPage.jsx           # Lead management, import, filtering
│   ├── CampaignsPage.jsx       # Campaign creation and tracking
│   ├── ContentPage.jsx         # AI content generation interface
│   └── AnalyticsPage.jsx       # Charts and insights
├── services/
│   └── api.js           # Axios-based API client with auth interceptors
└── hooks/
    └── useAuth.jsx      # Custom hook for authentication state
```

**State Management:**
- **Local State**: `useState` for component-level state
- **Authentication**: `useAuth` hook with localStorage for JWT persistence
- **API Calls**: Axios with automatic JWT token injection

**Routing Structure:**
- `/` → Login (if not authenticated)
- `/register` → User registration
- `/dashboard` → Main dashboard (protected)
- `/leads` → Lead management (protected)
- `/campaigns` → Campaign manager (protected)
- `/content` → AI content generator (protected)
- `/analytics` → Analytics dashboard (protected)

### AI Content Generation Flow

The AI content generation follows this flow:

1. **Frontend** (`ContentPage.jsx`): User enters topic, platform, tone
2. **API Request** → `POST /api/content/generate`
3. **Backend Route** (`content.py`): Validates request, extracts current user
4. **Service Layer** (`ai_content_generator.py`):
   - Constructs prompt based on content type (social post, email, ad)
   - Calls OpenRouter API with Claude 3.5 Sonnet
   - Parses JSON response from AI
5. **Database**: Saves generated content to `Content` model
6. **Response**: Returns formatted content to frontend
7. **Frontend**: Displays content with copy/edit options

**Important**: All AI-generated content requires human review before use (compliance requirement).

### Email Campaign Flow

Email campaigns follow strict consent compliance:

1. **Campaign Creation**: User creates campaign with subject/body
2. **Targeting**: User selects filters (sport type, customer type)
3. **Recipient Selection**: System filters leads WHERE `email_consent = true`
4. **Consent Verification**: Double-check consent date exists before sending
5. **Background Sending**: Emails sent asynchronously via `email_service.py`
6. **Tracking**: Campaign metrics updated (sent count, opens, clicks)
7. **Unsubscribe**: All emails include unsubscribe link (CAN-SPAM compliance)

**Never send emails to leads without `email_consent = true` and `consent_date`**.

## Development Workflow

### Adding a New API Endpoint

1. **Define Schema** in `backend/app/schemas/`:
   ```python
   # schemas/example.py
   from pydantic import BaseModel

   class ExampleCreate(BaseModel):
       field: str

   class ExampleResponse(BaseModel):
       id: int
       field: str

       class Config:
           from_attributes = True
   ```

2. **Create Model** in `backend/app/models/`:
   ```python
   # models/example.py
   from sqlalchemy import Column, Integer, String, ForeignKey
   from app.db.base import Base

   class Example(Base):
       __tablename__ = "examples"
       id = Column(Integer, primary_key=True, index=True)
       field = Column(String)
       user_id = Column(Integer, ForeignKey("users.id"))
   ```

3. **Add Route** in `backend/app/api/routes/`:
   ```python
   # api/routes/example.py
   from fastapi import APIRouter, Depends, HTTPException
   from sqlalchemy.orm import Session
   from app.db.session import get_db
   from app.core.security import get_current_user
   from app.models.user import User
   from app.models.example import Example
   from app.schemas.example import ExampleCreate, ExampleResponse

   router = APIRouter()

   @router.post("/", response_model=ExampleResponse)
   async def create_example(
       example: ExampleCreate,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user)
   ):
       db_example = Example(**example.dict(), user_id=current_user.id)
       db.add(db_example)
       db.commit()
       db.refresh(db_example)
       return db_example
   ```

4. **Register Router** in `backend/main.py`:
   ```python
   from app.api.routes import example
   app.include_router(example.router, prefix="/api/examples", tags=["Examples"])
   ```

### Adding a New Frontend Page

1. **Create Page Component** in `frontend/src/pages/`:
   ```jsx
   // pages/ExamplePage.jsx
   import { useState, useEffect } from 'react';
   import api from '../services/api';

   export default function ExamplePage() {
     const [data, setData] = useState([]);

     useEffect(() => {
       fetchData();
     }, []);

     const fetchData = async () => {
       const response = await api.get('/examples');
       setData(response.data);
     };

     return <div>...</div>;
   }
   ```

2. **Add Route** in `frontend/src/App.jsx`:
   ```jsx
   import ExamplePage from './pages/ExamplePage';

   // Inside Routes
   <Route path="/examples" element={<ExamplePage />} />
   ```

3. **Add Navigation** in `frontend/src/components/common/Sidebar.jsx`

## Important Compliance Notes

**This system is built compliance-first. Always maintain:**

1. **Consent Tracking**: Never contact leads without explicit opt-in
   - Check `email_consent = true` before sending emails
   - Check `sms_consent = true` before sending SMS
   - Track `consent_date` and `consent_source` for all leads

2. **Unsubscribe Mechanism**: All emails must include unsubscribe links
   - Template in `email_service.py` includes footer with unsubscribe
   - Unsubscribe requests immediately set `email_consent = false`

3. **Human Oversight**: AI-generated content requires manual review
   - Never auto-post AI content to social media
   - Never auto-send AI emails without user approval
   - Content is saved to database but not automatically published

4. **Data Privacy**:
   - Users can only access their own leads/campaigns
   - All routes use `get_current_user` dependency
   - Soft delete leads (set `is_active = false`) to maintain audit trail

## Testing Notes

When testing the system:

1. **Test User Creation**: Start by registering at `/register`
2. **Test Lead Import**: Use `docs/sample_leads.csv` for testing imports
3. **Test Consent**: Filter leads by consent status before campaigns
4. **Test AI Generation**: Requires valid `OPENROUTER_API_KEY` in `.env`
5. **Test Email Sending**: Requires valid SMTP credentials in `.env`

## Production Deployment

When deploying to production:

1. **Switch to PostgreSQL**: Update `DATABASE_URL` in `.env`
2. **Use Production SMTP**: Switch from Gmail to SendGrid/Mailgun
3. **Set Strong SECRET_KEY**: Generate new secret with `openssl rand -hex 32`
4. **Configure CORS**: Update `CORS_ORIGINS` to production domain
5. **Use Gunicorn**: Run with `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
6. **Build Frontend**: Run `npm run build` and serve from `dist/`

Refer to `docs/DEPLOYMENT.md` for detailed deployment instructions.

## Common Patterns in This Codebase

### Authentication Pattern
```python
# In route handlers
async def protected_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # current_user is automatically extracted from JWT token
    # Use current_user.id to associate data with the user
```

### Database Query Pattern
```python
# Get user's leads with filtering
leads = db.query(Lead).filter(
    Lead.user_id == current_user.id,
    Lead.email_consent == True
).all()
```

### API Client Pattern (Frontend)
```javascript
// In pages/components
import api from '../services/api';

// GET request
const response = await api.get('/leads');

// POST request
const response = await api.post('/leads', { name: 'John', email: 'john@example.com' });

// JWT token is automatically added to headers by interceptor in api.js
```

### Error Handling Pattern (Backend)
```python
from fastapi import HTTPException

if not resource:
    raise HTTPException(status_code=404, detail="Resource not found")

if not authorized:
    raise HTTPException(status_code=403, detail="Not authorized")
```

## AI Model Configuration

The system uses OpenRouter for flexibility across AI models:

- **Text Generation**: `anthropic/claude-3.5-sonnet` (default)
  - Used for: Social posts, emails, ad copy, content improvement
  - Can be changed in `.env` via `AI_MODEL_TEXT`

- **Image Prompts**: `stability-ai/stable-diffusion-xl`
  - Used for: Generating image prompts for visual content
  - Can be changed in `.env` via `AI_MODEL_IMAGE`

**Cost Management**: Monitor usage at https://openrouter.ai/activity
