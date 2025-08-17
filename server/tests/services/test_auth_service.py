import pytest
from unittest.mock import patch
from services.auth_service import AuthService

@pytest.mark.asyncio
class TestAuthService:
    @patch('services.auth_service.GoogleOAuthUtils.exchange_code_for_tokens')
    @patch('database.UserCrud.UserCRUD.get_user_by_google_id')
    @patch('database.UserCrud.UserCRUD.create_user')
    @patch('database.UserCrud.RefreshTokenCRUD.store_refresh_token')
    async def test_authenticate_with_authorization_code_new_user(self, mock_store_token, mock_create_user, mock_get_user, mock_exchange_tokens, mock_user_create, mock_user_db_result):
        mock_exchange_tokens.return_value = {
            "access_token": "fake_access_token",
            "refresh_token": "fake_refresh_token",
            "user_info": {
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
        }
        
        mock_get_user.return_value = None
        mock_create_user.return_value = mock_user_db_result
        mock_store_token.return_value = {"id": 1}
        
        result = await AuthService.authenticate_with_authorization_code("fake_auth_code", "http://localhost:8000/auth/callback")
        
        assert hasattr(result, "access_token")
        assert hasattr(result, "refresh_token")
        assert result.token_type == "bearer"
    
    @patch('services.auth_service.GoogleOAuthUtils.exchange_code_for_tokens')
    @patch('database.UserCrud.UserCRUD.get_user_by_google_id')
    @patch('database.UserCrud.RefreshTokenCRUD.store_refresh_token')
    async def test_authenticate_with_authorization_code_existing_user(self, mock_store_token, mock_get_user, mock_exchange_tokens, mock_user_create, mock_user_db_result):
        mock_exchange_tokens.return_value = {
            "access_token": "fake_access_token",
            "refresh_token": "fake_refresh_token",
            "user_info": {
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
        }
        
        mock_get_user.return_value = mock_user_db_result
        mock_store_token.return_value = {"id": 1}
        
        result = await AuthService.authenticate_with_authorization_code("fake_auth_code", "http://localhost:8000/auth/callback")
        
        assert hasattr(result, "access_token")
        assert hasattr(result, "refresh_token")
        assert result.token_type == "bearer"
    
    @patch('services.auth_service.GoogleOAuthUtils.exchange_code_for_tokens')
    async def test_authenticate_with_authorization_code_invalid_code(self, mock_exchange_tokens):
        mock_exchange_tokens.side_effect = Exception("Invalid code")
        
        with pytest.raises(Exception):
            await AuthService.authenticate_with_authorization_code("invalid_code", "http://localhost:8000/auth/callback") 