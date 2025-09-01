import pytest
from unittest.mock import Mock, patch
from services.redis.api_key_cache_service import ApiKeyCacheService

@pytest.fixture
def mock_redis_client():
    with patch('services.redis.base_redis_service.redis.Redis') as mock_redis:
        mock_client = Mock()
        mock_redis.return_value = mock_client
        yield mock_client

@pytest.fixture
def api_key_cache_service(mock_redis_client):
    return ApiKeyCacheService()

def test_get_api_key_cache_hit(api_key_cache_service, mock_redis_client):
    """Test successful cache retrieval"""
    mock_redis_client.hgetall.return_value = {
        "source_id": "123",
        "active": "true"
    }
    
    result = api_key_cache_service.get_api_key_cache("test_api_key")
    
    assert result is not None
    assert result["source_id"] == 123
    assert result["active"] is True
    mock_redis_client.hgetall.assert_called_once_with("api_key:test_api_key")

def test_get_api_key_cache_miss(api_key_cache_service, mock_redis_client):
    """Test cache miss scenario"""
    mock_redis_client.hgetall.return_value = {}
    
    result = api_key_cache_service.get_api_key_cache("test_api_key")
    
    assert result is None
    mock_redis_client.hgetall.assert_called_once_with("api_key:test_api_key")

def test_get_api_key_cache_inactive(api_key_cache_service, mock_redis_client):
    """Test cache retrieval for inactive source"""
    mock_redis_client.hgetall.return_value = {
        "source_id": "456",
        "active": "false"
    }
    
    result = api_key_cache_service.get_api_key_cache("test_api_key")
    
    assert result is not None
    assert result["source_id"] == 456
    assert result["active"] is False

def test_get_api_key_cache_redis_error(api_key_cache_service, mock_redis_client):
    """Test cache retrieval with Redis error"""
    mock_redis_client.hgetall.side_effect = Exception("Redis error")
    
    result = api_key_cache_service.get_api_key_cache("test_api_key")
    
    assert result is None

def test_set_api_key_cache(api_key_cache_service, mock_redis_client):
    """Test successful cache setting"""
    result = api_key_cache_service.set_api_key_cache("test_api_key", 123, True, 300)
    
    assert result is True
    mock_redis_client.hset.assert_called_once_with(
        "api_key:test_api_key", 
        mapping={"source_id": "123", "active": "true"}
    )
    mock_redis_client.expire.assert_called_once_with("api_key:test_api_key", 300)

def test_set_api_key_cache_inactive(api_key_cache_service, mock_redis_client):
    """Test cache setting for inactive source"""
    result = api_key_cache_service.set_api_key_cache("test_api_key", 456, False, 600)
    
    assert result is True
    mock_redis_client.hset.assert_called_once_with(
        "api_key:test_api_key", 
        mapping={"source_id": "456", "active": "false"}
    )
    mock_redis_client.expire.assert_called_once_with("api_key:test_api_key", 600)

def test_set_api_key_cache_redis_error(api_key_cache_service, mock_redis_client):
    """Test cache setting with Redis error"""
    mock_redis_client.hset.side_effect = Exception("Redis error")
    
    result = api_key_cache_service.set_api_key_cache("test_api_key", 123, True, 300)
    
    assert result is False

def test_invalidate_api_key_cache(api_key_cache_service, mock_redis_client):
    """Test successful cache invalidation"""
    result = api_key_cache_service.invalidate_api_key_cache("test_api_key")
    
    assert result is True
    mock_redis_client.delete.assert_called_once_with("api_key:test_api_key")

def test_invalidate_api_key_cache_redis_error(api_key_cache_service, mock_redis_client):
    """Test cache invalidation with Redis error"""
    mock_redis_client.delete.side_effect = Exception("Redis error")
    
    result = api_key_cache_service.invalidate_api_key_cache("test_api_key")
    
    assert result is False

def test_cache_key_format(api_key_cache_service, mock_redis_client):
    """Test that cache keys are formatted correctly"""
    mock_redis_client.hgetall.return_value = {"source_id": "123", "active": "true"}
    
    api_key_cache_service.get_api_key_cache("my-api-key-123")
    
    mock_redis_client.hgetall.assert_called_once_with("api_key:my-api-key-123")

def test_cache_data_types(api_key_cache_service, mock_redis_client):
    """Test that cache data types are handled correctly"""
    mock_redis_client.hgetall.return_value = {
        "source_id": "789",
        "active": "true"
    }
    
    result = api_key_cache_service.get_api_key_cache("test_api_key")
    
    assert isinstance(result["source_id"], int)
    assert isinstance(result["active"], bool)
    assert result["source_id"] == 789
    assert result["active"] is True 