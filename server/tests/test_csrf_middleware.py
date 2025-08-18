import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from middleware.csrf_middleware import CSRFMiddleware
import time

pytestmark = pytest.mark.enable_csrf

@pytest.fixture
def app():
    app = FastAPI()
    app.add_middleware(CSRFMiddleware, secret_key="test_secret_key")
    
    @app.get("/test-get")
    def test_get():
        return {"message": "success"}
    
    @app.post("/test-post")
    def test_post():
        return {"message": "success"}
    
    @app.head("/test-head")
    def test_head():
        return {"message": "success"}
    
    @app.options("/test-options")
    def test_options():
        return {"message": "success"}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_get_request_returns_csrf_token(client):
    response = client.get("/test-get")
    assert response.status_code == 200
    assert "X-CSRF-Token" in response.headers
    assert response.headers["X-CSRF-Token"] is not None

def test_post_request_without_csrf_token_fails(client):
    response = client.post("/test-post")
    assert response.status_code == 403
    assert "CSRF token validation failed" in response.json()["detail"]

def test_post_request_with_valid_csrf_token_succeeds(client):
    get_response = client.get("/test-get")
    csrf_token = get_response.headers["X-CSRF-Token"]
    
    response = client.post("/test-post", headers={"X-CSRF-Token": csrf_token})
    assert response.status_code == 200

def test_post_request_with_invalid_csrf_token_fails(client):
    response = client.post("/test-post", headers={"X-CSRF-Token": "invalid_token"})
    assert response.status_code == 403

def test_csrf_token_expiry(client):
    app = FastAPI()
    app.add_middleware(CSRFMiddleware, secret_key="test_secret_key", token_expiry=1)
    
    @app.get("/test-get")
    def test_get():
        return {"message": "success"}
    
    @app.post("/test-post")
    def test_post():
        return {"message": "success"}
    
    test_client = TestClient(app)
    
    get_response = test_client.get("/test-get")
    csrf_token = get_response.headers["X-CSRF-Token"]
    
    time.sleep(2)
    
    response = test_client.post("/test-post", headers={"X-CSRF-Token": csrf_token})
    assert response.status_code == 403

def test_safe_methods_dont_require_csrf_token(client):
    response = client.head("/test-head")
    assert response.status_code == 200
    
    response = client.options("/test-options")
    assert response.status_code == 200 