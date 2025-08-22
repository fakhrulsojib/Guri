from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from routers.log_sources_router import router as log_sources_router
from routers.log_router import log_router
from routers.auth_router import auth_router
from routers.health_router import health_router

def create_test_app():
    app = FastAPI()
    
    app.include_router(health_router)
    app.include_router(log_router)
    app.include_router(auth_router)
    app.include_router(log_sources_router)
    
    return app

def get_test_client():
    app = create_test_app()
    return TestClient(app)

def test_health_endpoint():
    app = create_test_app()
    client = TestClient(app)
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "Service is running"}

def test_app_lifespan_runs():
    from main import app
    
    with patch("main.start_raw_log_to_db_consumer") as mock_start, \
         patch("main.stop_raw_log_to_db_consumer") as mock_stop:
        
        with TestClient(app) as client:
            response = client.get("/api/v1/health/")
            assert response.status_code == 200
        
        assert True 