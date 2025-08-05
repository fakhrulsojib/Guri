import pytest
from unittest.mock import patch
from services.auth_service import AuthService

@pytest.mark.asyncio
class TestAuthService:
    @patch('services.auth_service.GoogleOAuthUtils.verify_google_token')
    @patch('database.UserCrud.UserCRUD.get_user_by_google_id')
    @patch('database.UserCrud.UserCRUD.create_user')
    @patch('database.UserCrud.RefreshTokenCRUD.store_refresh_token')
    async def test_authenticate_with_google_id_token_new_user(self, mock_store_token, mock_create_user, mock_get_user, mock_verify_token):
        mock_verify_token.return_value = {
            "user_id": "google123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/photo.jpg",
            "locale": "en",
            "hd": "example.com"
        }
        
        mock_get_user.return_value = None
        
        mock_user = {
            "id": 1,
            "email": "test@example.com",
            "google_id": "google123",
            "name": "Test User",
            "is_active": True
        }
        mock_create_user.return_value = mock_user
        
        mock_store_token.return_value = {"id": 1}
        
        result = await AuthService.authenticate_with_google_id_token("fake_google_token")
        
        assert hasattr(result, "access_token")
        assert hasattr(result, "refresh_token")
        assert result.token_type == "bearer"
    
    @patch('services.auth_service.GoogleOAuthUtils.verify_google_token')
    @patch('database.UserCrud.UserCRUD.get_user_by_google_id')
    @patch('database.UserCrud.RefreshTokenCRUD.store_refresh_token')
    async def test_authenticate_with_google_id_token_existing_user(self, mock_store_token, mock_get_user, mock_verify_token):
        mock_verify_token.return_value = {
            "user_id": "google123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/photo.jpg",
            "locale": "en",
            "hd": "example.com"
        }
        
        mock_user = {
            "id": 1,
            "email": "test@example.com",
            "google_id": "google123",
            "name": "Test User",
            "is_active": True
        }
        mock_get_user.return_value = mock_user
        
        mock_store_token.return_value = {"id": 1}
        
        result = await AuthService.authenticate_with_google_id_token("fake_google_token")
        
        assert hasattr(result, "access_token")
        assert hasattr(result, "refresh_token")
        assert result.token_type == "bearer"
    
    @patch('services.auth_service.GoogleOAuthUtils.verify_google_token')
    async def test_authenticate_with_google_id_token_invalid_token(self, mock_verify_token):
        mock_verify_token.side_effect = Exception("Invalid token")
        
        with pytest.raises(Exception):
            await AuthService.authenticate_with_google_id_token("invalid_token") 