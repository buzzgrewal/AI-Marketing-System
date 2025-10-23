from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings and configuration"""

    # App Info
    APP_NAME: str = "AI Marketing Automation System"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered marketing automation for cycling and triathlon businesses"

    # Database
    DATABASE_URL: str = "sqlite:///./marketing_automation.db"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenRouter API
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # AI Models
    AI_MODEL_TEXT: str = "anthropic/claude-3.5-sonnet"
    AI_MODEL_IMAGE: str = "google/gemini-2.5-flash-image"

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "AI Marketing System"

    # Shopify Integration
    SHOPIFY_STORE_URL_1: str = ""
    SHOPIFY_API_KEY_1: str = ""
    SHOPIFY_ACCESS_TOKEN_1: str = ""
    SHOPIFY_STORE_URL_2: str = ""
    SHOPIFY_API_KEY_2: str = ""
    SHOPIFY_ACCESS_TOKEN_2: str = ""

    # Meta/Facebook Configuration
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_ACCESS_TOKEN: str = ""

    # Google Analytics
    GA_MEASUREMENT_ID: str = ""
    GA_API_SECRET: str = ""

    # Application URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
