from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_app_lifespan_runs():
    with patch("main.start_raw_log_to_db_consumer") as mock_start, \
         patch("main.stop_raw_log_to_db_consumer") as mock_stop:
        with TestClient(app) as client:
            response = client.get("/api/v1/health/")
            assert response.status_code == 200
        mock_start.assert_called_once()
        mock_stop.assert_called_once() 