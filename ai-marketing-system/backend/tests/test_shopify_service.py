import pytest
from app.services.shopify_service import ShopifyService


@pytest.fixture
def shopify_service():
    """Create a ShopifyService instance for testing"""
    return ShopifyService()


def test_shopify_service_initialization(shopify_service):
    """Test that ShopifyService initializes correctly"""
    assert shopify_service is not None
    assert len(shopify_service.stores) == 2


def test_get_all_stores(shopify_service):
    """Test getting all stores"""
    stores = shopify_service.get_all_stores()
    assert len(stores) == 2
    assert stores[0]['name'] == 'Premier Bike'
    assert stores[1]['name'] == 'Position One Sports'


def test_get_store_config(shopify_service):
    """Test getting store configuration"""
    store_1 = shopify_service._get_store_config(1)
    assert store_1 is not None
    assert store_1['id'] == 1
    assert store_1['name'] == 'Premier Bike'

    store_2 = shopify_service._get_store_config(2)
    assert store_2 is not None
    assert store_2['id'] == 2
    assert store_2['name'] == 'Position One Sports'


def test_get_invalid_store_config(shopify_service):
    """Test getting config for non-existent store"""
    store = shopify_service._get_store_config(999)
    assert store is None


def test_is_store_configured(shopify_service):
    """Test store configuration check"""
    # Create a mock store with valid config
    valid_store = {
        "store_url": "example.myshopify.com",
        "access_token": "valid-token-123"
    }
    assert shopify_service._is_store_configured(valid_store) is True

    # Create a mock store with invalid config
    invalid_store = {
        "store_url": "",
        "access_token": "your-shopify-access-token"
    }
    assert shopify_service._is_store_configured(invalid_store) is False


@pytest.mark.asyncio
async def test_get_store_info_unconfigured(shopify_service):
    """Test getting store info for unconfigured store"""
    # This will return info indicating store is not configured
    result = await shopify_service.get_store_info(1)
    assert result is not None
    assert result['id'] == 1
    assert 'configured' in result


def test_store_urls(shopify_service):
    """Test that store URLs are properly configured"""
    stores = shopify_service.get_all_stores()
    assert stores[0]['store_url'] == 'premierbike.myshopify.com'
    assert stores[1]['store_url'] == 'positiononesports.myshopify.com'
