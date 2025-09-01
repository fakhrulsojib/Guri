import pytest
from unittest.mock import Mock, patch
from services.redis.base_redis_service import BaseRedisService
import redis

@pytest.fixture
def mock_redis_client():
    with patch('services.redis.base_redis_service.redis.Redis') as mock_redis:
        mock_client = Mock()
        mock_redis.return_value = mock_client
        yield mock_client

@pytest.fixture
def base_redis_service(mock_redis_client):
    return BaseRedisService()

def test_base_redis_service_initialization(base_redis_service, mock_redis_client):
    """Test that BaseRedisService initializes with correct configuration"""
    assert base_redis_service.redis_host == "redis"
    assert base_redis_service.redis_port == 6379
    assert base_redis_service.redis_db == 0
    assert base_redis_service.redis_password is None

def test_base_redis_service_with_custom_config():
    """Test BaseRedisService with custom environment variables"""
    with patch.dict('os.environ', {
        'REDIS_HOST': 'custom-host',
        'REDIS_PORT': '6380',
        'REDIS_DB': '1',
        'REDIS_PASSWORD': 'custom-password'
    }):
        with patch('services.redis.base_redis_service.redis.Redis') as mock_redis:
            service = BaseRedisService()
            assert service.redis_host == "custom-host"
            assert service.redis_port == 6380
            assert service.redis_db == 1
            assert service.redis_password == "custom-password"

def test_health_check_success(base_redis_service, mock_redis_client):
    """Test successful health check"""
    mock_redis_client.ping.return_value = True
    
    result = base_redis_service.health_check()
    
    assert result is True
    mock_redis_client.ping.assert_called_once()

def test_health_check_failure(base_redis_service, mock_redis_client):
    """Test health check failure"""
    mock_redis_client.ping.side_effect = Exception("Connection failed")
    
    result = base_redis_service.health_check()
    
    assert result is False

def test_health_check_redis_error(base_redis_service, mock_redis_client):
    """Test health check with Redis-specific error"""
    mock_redis_client.ping.side_effect = redis.ConnectionError("Redis connection error")
    
    result = base_redis_service.health_check()
    
    assert result is False

def test_health_check_timeout_error(base_redis_service, mock_redis_client):
    """Test health check with timeout error"""
    mock_redis_client.ping.side_effect = redis.TimeoutError("Redis timeout")
    
    result = base_redis_service.health_check()
    
    assert result is False 