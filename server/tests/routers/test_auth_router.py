from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

class TestAuthRouter:
    @patch('services.auth_service.GoogleOAuthUtils.verify_google_token')
    @patch('database.UserCrud.UserCRUD.get_user_by_google_id')
    @patch('database.UserCrud.UserCRUD.create_user')
    @patch('database.UserCrud.RefreshTokenCRUD.store_refresh_token')
    def test_google_login_new_user(self, mock_store_token, mock_create_user, mock_get_user, mock_verify_token, mock_user_create, mock_user_db_result):
        mock_verify_token.return_value = {
            "user_id": mock_user_create["google_id"],
            "email": mock_user_create["email"],
            "email_verified": mock_user_create["email_verified"],
            "name": mock_user_create["name"],
            "given_name": mock_user_create["given_name"],
            "family_name": mock_user_create["family_name"],
            "picture": mock_user_create["picture"],
            "locale": mock_user_create["locale"],
            "hd": mock_user_create["hd"]
        }
        
        mock_get_user.return_value = None
        mock_create_user.return_value = mock_user_db_result
        mock_store_token.return_value = {"id": 1}
        
        response = client.post("/auth/google/login", json={
            "id_token": "fake_google_token"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @patch('services.auth_service.GoogleOAuthUtils.verify_google_token')
    @patch('database.UserCrud.UserCRUD.get_user_by_google_id')
    @patch('database.UserCrud.RefreshTokenCRUD.store_refresh_token')
    def test_google_login_existing_user(self, mock_store_token, mock_get_user, mock_verify_token, mock_user_create, mock_user_db_result):
        mock_verify_token.return_value = {
            "user_id": mock_user_create["google_id"],
            "email": mock_user_create["email"],
            "email_verified": mock_user_create["email_verified"],
            "name": mock_user_create["name"],
            "given_name": mock_user_create["given_name"],
            "family_name": mock_user_create["family_name"],
            "picture": mock_user_create["picture"],
            "locale": mock_user_create["locale"],
            "hd": mock_user_create["hd"]
        }
        
        mock_get_user.return_value = mock_user_db_result
        mock_store_token.return_value = {"id": 1}
        
        response = client.post("/auth/google/login", json={
            "id_token": "fake_google_token"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_google_login_missing_token(self):
        response = client.post("/auth/google/login", json={})
        assert response.status_code == 400

class TestProtectedEndpoints:
    def test_me_endpoint_without_token(self):
        response = client.get("/auth/me")
        assert response.status_code == 403
    
    def test_me_endpoint_with_invalid_token(self):
        response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401

class TestTokenRefresh:
    def test_refresh_without_token(self):
        response = client.post("/auth/refresh", json={})
        assert response.status_code == 422
    
    def test_refresh_with_invalid_token(self):
        response = client.post("/auth/refresh", json={"refresh_token": "invalid_token"})
        assert response.status_code == 401

class TestLogout:
    def test_logout_without_token(self):
        response = client.post("/auth/logout", json={})
        assert response.status_code == 422
    
    def test_logout_with_invalid_token(self):
        response = client.post("/auth/logout", json={"refresh_token": "invalid_token"})
        assert response.status_code == 200 