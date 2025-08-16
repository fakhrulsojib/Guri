import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException
from google.auth.exceptions import GoogleAuthError
import httpx

from util.google_oauth import GoogleOAuthUtils, GoogleOAuthConfig

class TestGoogleOAuthConfig:
    def test_config_loading(self):
        assert hasattr(GoogleOAuthConfig, 'CLIENT_ID')
        assert hasattr(GoogleOAuthConfig, 'CLIENT_SECRET')
        assert hasattr(GoogleOAuthConfig, 'GOOGLE_TOKEN_INFO_URL')
        assert hasattr(GoogleOAuthConfig, 'GOOGLE_USER_INFO_URL')

@pytest.mark.asyncio
class TestGoogleOAuthUtils:
    @patch('util.google_oauth.id_token.verify_oauth2_token')
    @patch('util.google_oauth.requests.Request')
    async def test_verify_google_token_success(self, mock_request, mock_verify_token):
        mock_verify_token.return_value = {
            'aud': 'test_client_id',
            'sub': 'google123',
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'https://example.com/photo.jpg',
            'locale': 'en',
            'hd': 'example.com',
            'exp': 9999999999
        }
        mock_request.return_value.time = 1000000000

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            result = await GoogleOAuthUtils.verify_google_token('fake_id_token')

        assert result['user_id'] == 'google123'
        assert result['email'] == 'test@example.com'
        assert result['email_verified'] is True
        assert result['name'] == 'Test User'
        assert result['given_name'] == 'Test'
        assert result['family_name'] == 'User'
        assert result['picture'] == 'https://example.com/photo.jpg'
        assert result['locale'] == 'en'
        assert result['hd'] == 'example.com'

    @patch('util.google_oauth.id_token.verify_oauth2_token')
    @patch('util.google_oauth.requests.Request')
    async def test_verify_google_token_invalid_audience(self, mock_request, mock_verify_token):
        mock_verify_token.return_value = {
            'aud': 'wrong_client_id',
            'sub': 'google123',
            'email': 'test@example.com',
            'exp': 9999999999
        }
        mock_request.return_value.time = 1000000000

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            with pytest.raises(HTTPException) as exc_info:
                await GoogleOAuthUtils.verify_google_token('fake_id_token')

        assert exc_info.value.status_code == 401
        assert "Invalid token audience" in str(exc_info.value.detail)

    @patch('util.google_oauth.id_token.verify_oauth2_token')
    @patch('util.google_oauth.requests.Request')
    async def test_verify_google_token_expired(self, mock_request, mock_verify_token):
        mock_verify_token.return_value = {
            'aud': 'test_client_id',
            'sub': 'google123',
            'email': 'test@example.com',
            'exp': 1000000000
        }
        mock_request.return_value.time = 9999999999

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            with pytest.raises(HTTPException) as exc_info:
                await GoogleOAuthUtils.verify_google_token('fake_id_token')

        assert exc_info.value.status_code == 401
        assert "Token has expired" in str(exc_info.value.detail)

    @patch('util.google_oauth.id_token.verify_oauth2_token')
    async def test_verify_google_token_google_auth_error(self, mock_verify_token):
        mock_verify_token.side_effect = GoogleAuthError("Invalid token")

        with pytest.raises(HTTPException) as exc_info:
            await GoogleOAuthUtils.verify_google_token('invalid_token')

        assert exc_info.value.status_code == 401
        assert "Invalid Google token" in str(exc_info.value.detail)

    @patch('util.google_oauth.id_token.verify_oauth2_token')
    async def test_verify_google_token_general_exception(self, mock_verify_token):
        mock_verify_token.side_effect = Exception("Unexpected error")

        with pytest.raises(HTTPException) as exc_info:
            await GoogleOAuthUtils.verify_google_token('invalid_token')

        assert exc_info.value.status_code == 401
        assert "Token verification failed" in str(exc_info.value.detail)

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_verify_access_token_success(self, mock_client):
        mock_response_token = MagicMock()
        mock_response_token.status_code = 200
        mock_response_token.json.return_value = {
            'aud': 'test_client_id',
            'exp': 9999999999
        }

        mock_response_user = MagicMock()
        mock_response_user.status_code = 200
        mock_response_user.json.return_value = {
            'id': 'google123',
            'email': 'test@example.com',
            'verified_email': True,
            'name': 'Test User',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'https://example.com/photo.jpg',
            'locale': 'en',
            'hd': 'example.com'
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.side_effect = [mock_response_token, mock_response_user]
        mock_client.return_value = mock_client_instance

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            result = await GoogleOAuthUtils.verify_access_token('fake_access_token')

        assert result['user_id'] == 'google123'
        assert result['email'] == 'test@example.com'
        assert result['email_verified'] is True
        assert result['name'] == 'Test User'
        assert result['given_name'] == 'Test'
        assert result['family_name'] == 'User'
        assert result['picture'] == 'https://example.com/photo.jpg'
        assert result['locale'] == 'en'
        assert result['hd'] == 'example.com'

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_verify_access_token_invalid_token_response(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 400

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        with pytest.raises(HTTPException) as exc_info:
            await GoogleOAuthUtils.verify_access_token('invalid_token')

        assert exc_info.value.status_code == 401
        assert "Invalid access token" in str(exc_info.value.detail)

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_verify_access_token_invalid_audience(self, mock_client):
        mock_response_token = MagicMock()
        mock_response_token.status_code = 200
        mock_response_token.json.return_value = {
            'aud': 'wrong_client_id',
            'exp': 9999999999
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.return_value = mock_response_token
        mock_client.return_value = mock_client_instance

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            with pytest.raises(HTTPException) as exc_info:
                await GoogleOAuthUtils.verify_access_token('fake_access_token')

        assert exc_info.value.status_code == 401
        assert "Invalid token audience" in str(exc_info.value.detail)

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_verify_access_token_user_info_failed(self, mock_client):
        mock_response_token = MagicMock()
        mock_response_token.status_code = 200
        mock_response_token.json.return_value = {
            'aud': 'test_client_id',
            'exp': 9999999999
        }

        mock_response_user = MagicMock()
        mock_response_user.status_code = 400

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.side_effect = [mock_response_token, mock_response_user]
        mock_client.return_value = mock_client_instance

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            with pytest.raises(HTTPException) as exc_info:
                await GoogleOAuthUtils.verify_access_token('fake_access_token')

        assert exc_info.value.status_code == 401
        assert "Failed to get user information" in str(exc_info.value.detail)

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_verify_access_token_request_error(self, mock_client):
        mock_client.side_effect = httpx.RequestError("Network error")

        with pytest.raises(HTTPException) as exc_info:
            await GoogleOAuthUtils.verify_access_token('fake_access_token')

        assert exc_info.value.status_code == 500
        assert "Failed to verify token" in str(exc_info.value.detail)

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_exchange_code_for_tokens_success(self, mock_client):
        mock_response_token = MagicMock()
        mock_response_token.status_code = 200
        mock_response_token.json.return_value = {
            'access_token': 'fake_access_token',
            'refresh_token': 'fake_refresh_token'
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.post.return_value = mock_response_token
        mock_client.return_value = mock_client_instance

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            with patch.object(GoogleOAuthConfig, 'CLIENT_SECRET', 'test_client_secret'):
                with patch.object(GoogleOAuthUtils, 'verify_access_token') as mock_verify:
                    mock_verify.return_value = {
                        'user_id': 'google123',
                        'email': 'test@example.com',
                        'name': 'Test User'
                    }

                    result = await GoogleOAuthUtils.exchange_code_for_tokens(
                        'fake_auth_code', 'http://localhost/callback'
                    )

        assert result['access_token'] == 'fake_access_token'
        assert result['refresh_token'] == 'fake_refresh_token'
        assert 'user_info' in result

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_exchange_code_for_tokens_failed_exchange(self, mock_client):
        mock_response = MagicMock()
        mock_response.status_code = 400

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance

        with pytest.raises(HTTPException) as exc_info:
            await GoogleOAuthUtils.exchange_code_for_tokens(
                'invalid_code', 'http://localhost/callback'
            )

        assert exc_info.value.status_code == 400
        assert "Failed to exchange code for tokens" in str(exc_info.value.detail)

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_exchange_code_for_tokens_request_error(self, mock_client):
        mock_client.side_effect = httpx.RequestError("Network error")

        with pytest.raises(HTTPException) as exc_info:
            await GoogleOAuthUtils.exchange_code_for_tokens(
                'fake_code', 'http://localhost/callback'
            )

        assert exc_info.value.status_code == 500
        assert "Failed to exchange tokens" in str(exc_info.value.detail)

    @patch('util.google_oauth.httpx.AsyncClient')
    async def test_exchange_code_for_tokens_general_exception(self, mock_client):
        mock_client.side_effect = Exception("Unexpected error")

        with pytest.raises(HTTPException) as exc_info:
            await GoogleOAuthUtils.exchange_code_for_tokens(
                'fake_code', 'http://localhost/callback'
            )

        assert exc_info.value.status_code == 400
        assert "Token exchange failed" in str(exc_info.value.detail) 