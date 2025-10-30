from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.routes import auth, leads, campaigns, content, email_templates, social_scheduling, segments, ab_tests, webhooks, shopify, facebook_leads, lead_forms

# Import models to ensure tables are created
from app.models import lead_form  # noqa: F401

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for uploaded images
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(content.router, prefix="/api/content", tags=["Content Generation"])
app.include_router(email_templates.router, prefix="/api/templates", tags=["Email Templates"])
app.include_router(social_scheduling.router, prefix="/api/schedule", tags=["Social Media Scheduling"])
app.include_router(segments.router, prefix="/api/segments", tags=["Segments"])
app.include_router(ab_tests.router, prefix="/api/ab-tests", tags=["A/B Testing"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(shopify.router, prefix="/api/shopify", tags=["Shopify Integration"])
app.include_router(facebook_leads.router, prefix="/api/facebook-leads", tags=["Facebook Lead Ads"])
app.include_router(lead_forms.router, prefix="/api/forms", tags=["Lead Forms"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Marketing Automation System API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
