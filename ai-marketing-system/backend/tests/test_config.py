import pytest
from app.core.config import Settings


def test_settings_creation():
    """Test that settings can be created with defaults"""
    settings = Settings()
    assert settings.APP_NAME == "AI Marketing Automation System"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30


def test_shopify_stores_configured():
    """Test Shopify store configuration exists"""
    settings = Settings()
    assert hasattr(settings, 'SHOPIFY_STORE_URL_1')
    assert hasattr(settings, 'SHOPIFY_STORE_URL_2')
    assert hasattr(settings, 'SHOPIFY_API_KEY_1')
    assert hasattr(settings, 'SHOPIFY_ACCESS_TOKEN_1')


def test_ai_models_configured():
    """Test AI model configuration"""
    settings = Settings()
    assert settings.AI_MODEL_TEXT is not None
    assert settings.AI_MODEL_IMAGE is not None
    assert settings.OPENROUTER_BASE_URL == "https://openrouter.ai/api/v1"


def test_cors_origins():
    """Test CORS configuration"""
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) > 0
