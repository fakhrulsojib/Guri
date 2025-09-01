from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from model.log_sources import LogSourceInDB, LogSourceStatus
from main import app
import json

SINGLE_LOG_API_ENDPOINT = "/api/v1/logs"

client = TestClient(app)

@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.producer")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_accepts_valid_json(mock_get_source, mock_producer, mock_redis_cache, mock_log_source, mock_raw_log):
    # Create a proper LogSourceInDB object for the mock
    log_source_obj = LogSourceInDB(**mock_log_source)
    mock_redis_cache.return_value = None
    mock_get_source.return_value = log_source_obj
    
    mock_producer.produce = MagicMock()
    mock_producer.flush = MagicMock()
    
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=mock_raw_log)
    assert response.status_code == 201
    assert "status" in response.json()
    
    mock_producer.produce.assert_called_once()
    call_args = mock_producer.produce.call_args
    kafka_value = json.loads(call_args[1]['value'].decode('utf-8'))
    assert 'source_id' in kafka_value
    assert kafka_value['source_id'] == mock_log_source["id"]
    assert 'api_key' not in kafka_value

@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.producer")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_accepts_minimal_data(mock_get_source, mock_producer, mock_redis_cache, mock_log_source, mock_raw_log_minimal):
    # Create a proper LogSourceInDB object for the mock
    log_source_obj = LogSourceInDB(**mock_log_source)
    mock_redis_cache.return_value = None
    mock_get_source.return_value = log_source_obj
    
    mock_producer.produce = MagicMock()
    mock_producer.flush = MagicMock()
    
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=mock_raw_log_minimal)
    assert response.status_code == 201
    assert "status" in response.json()
    
    mock_producer.produce.assert_called_once()
    call_args = mock_producer.produce.call_args
    kafka_value = json.loads(call_args[1]['value'].decode('utf-8'))
    assert 'source_id' in kafka_value
    assert kafka_value['source_id'] == mock_log_source["id"]
    assert 'api_key' not in kafka_value

@patch("routers.log_router.producer")
def test_log_rejects_empty_body(mock_producer):
    response = client.post(SINGLE_LOG_API_ENDPOINT, content="")
    assert response.status_code == 422
    assert "detail" in response.json()

@patch("routers.log_router.producer")
def test_log_rejects_malformed_json(mock_producer):
    response = client.post(SINGLE_LOG_API_ENDPOINT, content="{invalid json")
    assert response.status_code == 422

@patch("routers.log_router.producer")
def test_log_rejects_plain_text(mock_producer):
    response = client.post(SINGLE_LOG_API_ENDPOINT, content="plain text log")
    assert response.status_code == 422
    assert "detail" in response.json()

@patch("routers.log_router.producer")
def test_log_rejects_missing_required_fields(mock_producer):
    incomplete_data = {"api_key": "test_key"}
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=incomplete_data)
    assert response.status_code == 422

@patch("routers.log_router.producer")
def test_log_rejects_invalid_api_key(mock_producer, mock_raw_log):
    invalid_data = mock_raw_log.copy()
    invalid_data["api_key"] = ""
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=invalid_data)
    assert response.status_code == 422

@patch("routers.log_router.producer")
@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_rejects_nonexistent_api_key(mock_get_source, mock_redis_cache, mock_producer, mock_raw_log):
    """Test that logs with non-existent API keys are rejected"""
    mock_redis_cache.return_value = None
    mock_get_source.return_value = None
    
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=mock_raw_log)
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]

@patch("routers.log_router.producer")
@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_rejects_inactive_log_source(mock_get_source, mock_redis_cache, mock_producer, mock_inactive_log_source, mock_raw_log):
    """Test that logs from inactive log sources are rejected"""
    mock_redis_cache.return_value = None
    # Create a proper LogSourceInDB object for the mock
    log_source_obj = LogSourceInDB(**mock_inactive_log_source)
    mock_get_source.return_value = log_source_obj
    
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=mock_raw_log)
    assert response.status_code == 403
    assert "not active" in response.json()["detail"]

@patch("routers.log_router.producer")
def test_log_rejects_invalid_level(mock_producer, mock_raw_log):
    invalid_data = mock_raw_log.copy()
    invalid_data["level"] = "INVALID_LEVEL"
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=invalid_data)
    assert response.status_code == 422

@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.producer")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_accepts_all_valid_levels(mock_get_source, mock_producer, mock_redis_cache, mock_log_source):
    # Create a proper LogSourceInDB object for the mock
    log_source_obj = LogSourceInDB(**mock_log_source)
    mock_redis_cache.return_value = None
    mock_get_source.return_value = log_source_obj
    
    mock_producer.produce = MagicMock()
    mock_producer.flush = MagicMock()
    
    for level in ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]:
        log_data = {
            "api_key": "test_api_key_12345",
            "message": f"Test {level} message",
            "level": level
        }
        response = client.post(SINGLE_LOG_API_ENDPOINT, json=log_data)
        assert response.status_code == 201

@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.producer")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_rejects_oversized_payload(mock_get_source, mock_producer, mock_redis_cache, mock_log_source):
    # Create a proper LogSourceInDB object for the mock
    log_source_obj = LogSourceInDB(**mock_log_source)
    mock_redis_cache.return_value = None
    mock_get_source.return_value = log_source_obj
    
    large_data = {
        "api_key": "test_api_key_12345",
        "message": "x" * 1000000,
        "data": {"large_field": "x" * 500000}
    }
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=large_data)
    assert response.status_code == 413

@patch("routers.log_router.producer")
def test_log_rejects_get_method(mock_producer):
    response = client.get(SINGLE_LOG_API_ENDPOINT)
    assert response.status_code == 405

@patch("routers.log_router.producer")
def test_log_wrong_path(mock_producer, mock_raw_log):
    response = client.post("/api/v1/log/", json=mock_raw_log)
    assert response.status_code == 404

@patch("routers.log_router.producer")
def test_log_validates_timestamp_format(mock_producer):
    invalid_timestamp_data = {
        "api_key": "test_api_key_12345",
        "message": "test message",
        "timestamp": "invalid-timestamp"
    }
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=invalid_timestamp_data)
    assert response.status_code == 422

@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.producer")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_accepts_valid_timestamp(mock_get_source, mock_producer, mock_redis_cache, mock_log_source):
    # Create a proper LogSourceInDB object for the mock
    log_source_obj = LogSourceInDB(**mock_log_source)
    mock_redis_cache.return_value = None
    mock_get_source.return_value = log_source_obj
    
    mock_producer.produce = MagicMock()
    mock_producer.flush = MagicMock()
    
    valid_timestamp_data = {
        "api_key": "test_api_key_12345",
        "message": "test message",
        "timestamp": "2023-07-25T10:30:00.123Z"
    }
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=valid_timestamp_data)
    assert response.status_code == 201

@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.producer")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_accepts_json_data_and_metadata(mock_get_source, mock_producer, mock_redis_cache, mock_log_source):
    # Create a proper LogSourceInDB object for the mock
    log_source_obj = LogSourceInDB(**mock_log_source)
    mock_redis_cache.return_value = None
    mock_get_source.return_value = log_source_obj
    
    mock_producer.produce = MagicMock()
    mock_producer.flush = MagicMock()
    
    complex_data = {
        "api_key": "test_api_key_12345",
        "message": "Complex log entry",
        "data": {
            "user_id": 123,
            "action": "login",
            "ip_address": "192.168.1.1",
            "nested": {
                "level1": {
                    "level2": "deep_value"
                }
            }
        },
        "metadata": {
            "service": "auth-service",
            "version": "2.1.0",
            "environment": "production",
            "tags": ["security", "authentication"]
        }
    }
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=complex_data)
    assert response.status_code == 201

@patch("routers.log_router.api_key_cache_service.get_api_key_cache")
@patch("routers.log_router.producer")
@patch("routers.log_router.LogSourceService.get_log_source_by_api_key")
def test_log_accepts_trace_and_span_ids(mock_get_source, mock_producer, mock_redis_cache, mock_log_source):
    # Create a proper LogSourceInDB object for the mock
    log_source_obj = LogSourceInDB(**mock_log_source)
    mock_redis_cache.return_value = None
    mock_get_source.return_value = log_source_obj
    
    mock_producer.produce = MagicMock()
    mock_producer.flush = MagicMock()
    
    trace_data = {
        "api_key": "test_api_key_12345",
        "message": "Traced log entry",
        "trace_id": "trace-abc-123-def-456",
        "span_id": "span-xyz-789"
    }
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=trace_data)
    assert response.status_code == 201
