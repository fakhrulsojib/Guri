from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

SINGLE_LOG_API_ENDPOINT = "/api/v1/log/"

valid_log_data = {
    "provider": "test-service",
    "data": "Test log message",
    "timestamp": "2023-07-25T10:30:00Z"
}

client = TestClient(app)

@patch("routers.log_router.producer")
def test_log_accepts_valid_json(mock_producer):
    mock_producer.produce = MagicMock()
    mock_producer.flush = MagicMock()
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=valid_log_data)
    assert response.status_code == 201
    assert "status" in response.json()

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
    incomplete_data = {"provider": "test"}
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=incomplete_data)
    assert response.status_code == 422

@patch("routers.log_router.producer")
def test_log_rejects_oversized_payload(mock_producer):
    large_data = {
        "provider": "test",
        "data": "x" * 1000000,
        "timestamp": "2023-07-25T10:30:00Z"
    }
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=large_data)
    assert response.status_code == 413

@patch("routers.log_router.producer")
def test_log_rejects_get_method(mock_producer):
    response = client.get(SINGLE_LOG_API_ENDPOINT)
    assert response.status_code == 405

@patch("routers.log_router.producer")
def test_log_wrong_path(mock_producer):
    response = client.post("/api/v1/logs/", json=valid_log_data)
    assert response.status_code == 404

@patch("routers.log_router.producer")
def test_log_validates_timestamp_format(mock_producer):
    invalid_timestamp_data = {
        "provider": "test",
        "data": "test message",
        "timestamp": "invalid-timestamp"
    }
    response = client.post(SINGLE_LOG_API_ENDPOINT, json=invalid_timestamp_data)
    assert response.status_code == 422
