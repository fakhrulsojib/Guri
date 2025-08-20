from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

class TestProtectedEndpoints:
    def setup_method(self):
        """Clear cookies before each test"""
        client.cookies.clear()
    
    def test_me_endpoint_without_cookies(self):
        response = client.get("/auth/me")
        assert response.status_code == 401
    
    def test_me_endpoint_with_invalid_cookies(self):
        client.cookies.set("access_token", "invalid_token")
        response = client.get("/auth/me")
        assert response.status_code == 401

class TestTokenRefresh:
    def setup_method(self):
        """Clear cookies before each test"""
        client.cookies.clear()
    
    def test_refresh_without_cookies(self):
        response = client.post("/auth/refresh")
        assert response.status_code == 401
    
    def test_refresh_with_invalid_cookies(self):
        client.cookies.set("refresh_token", "invalid_token")
        response = client.post("/auth/refresh")
        assert response.status_code == 401

class TestLogout:
    def setup_method(self):
        """Clear cookies before each test"""
        client.cookies.clear()
    
    def test_logout_without_cookies(self):
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"message": "Successfully logged out"}
    
    def test_logout_with_invalid_cookies(self):
        client.cookies.set("refresh_token", "invalid_token")
        response = client.post("/auth/logout")
        assert response.status_code == 200 