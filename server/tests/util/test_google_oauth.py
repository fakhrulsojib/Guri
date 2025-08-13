import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException
from google.auth.exceptions import GoogleAuthError
import httpx

from util.google_oauth import GoogleOAuthUtils, GoogleOAuthConfig

@pytest.fixture
def mock_google_token_data():
    """Test data for Google token verification"""
    return {
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

@pytest.fixture
def mock_google_user_info():
    """Test data for Google user information"""
    return {
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

@pytest.fixture
def mock_token_exchange_response():
    """Test data for token exchange response"""
    return {
        'access_token': 'fake_access_token',
        'refresh_token': 'fake_refresh_token'
    }

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
    async def test_verify_google_token_success(self, mock_request, mock_verify_token, mock_google_token_data):
        mock_verify_token.return_value = mock_google_token_data
        mock_request.return_value.time = 1000000000

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            result = await GoogleOAuthUtils.verify_google_token('fake_id_token')

        assert result['user_id'] == mock_google_token_data['sub']
        assert result['email'] == mock_google_token_data['email']
        assert result['email_verified'] == mock_google_token_data['email_verified']
        assert result['name'] == mock_google_token_data['name']
        assert result['given_name'] == mock_google_token_data['given_name']
        assert result['family_name'] == mock_google_token_data['family_name']
        assert result['picture'] == mock_google_token_data['picture']
        assert result['locale'] == mock_google_token_data['locale']
        assert result['hd'] == mock_google_token_data['hd']

    @patch('util.google_oauth.id_token.verify_oauth2_token')
    @patch('util.google_oauth.requests.Request')
    async def test_verify_google_token_invalid_audience(self, mock_request, mock_verify_token, mock_google_token_data):
        token_data = mock_google_token_data.copy()
        token_data['aud'] = 'wrong_client_id'
        mock_verify_token.return_value = token_data
        mock_request.return_value.time = 1000000000

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            with pytest.raises(HTTPException) as exc_info:
                await GoogleOAuthUtils.verify_google_token('fake_id_token')

        assert exc_info.value.status_code == 401
        assert "Invalid token audience" in str(exc_info.value.detail)

    @patch('util.google_oauth.id_token.verify_oauth2_token')
    @patch('util.google_oauth.requests.Request')
    async def test_verify_google_token_expired(self, mock_request, mock_verify_token, mock_google_token_data):
        token_data = mock_google_token_data.copy()
        token_data['exp'] = 1000000000
        mock_verify_token.return_value = token_data
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
    async def test_verify_access_token_success(self, mock_client, mock_google_user_info):
        mock_response_token = MagicMock()
        mock_response_token.status_code = 200
        mock_response_token.json.return_value = {
            'aud': 'test_client_id',
            'exp': 9999999999
        }

        mock_response_user = MagicMock()
        mock_response_user.status_code = 200
        mock_response_user.json.return_value = mock_google_user_info

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.side_effect = [mock_response_token, mock_response_user]
        mock_client.return_value = mock_client_instance

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            result = await GoogleOAuthUtils.verify_access_token('fake_access_token')

        assert result['user_id'] == mock_google_user_info['id']
        assert result['email'] == mock_google_user_info['email']
        assert result['email_verified'] == mock_google_user_info['verified_email']
        assert result['name'] == mock_google_user_info['name']
        assert result['given_name'] == mock_google_user_info['given_name']
        assert result['family_name'] == mock_google_user_info['family_name']
        assert result['picture'] == mock_google_user_info['picture']
        assert result['locale'] == mock_google_user_info['locale']
        assert result['hd'] == mock_google_user_info['hd']

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
    async def test_exchange_code_for_tokens_success(self, mock_client, mock_google_user_info, mock_token_exchange_response):
        mock_response_token = MagicMock()
        mock_response_token.status_code = 200
        mock_response_token.json.return_value = mock_token_exchange_response

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.post.return_value = mock_response_token
        mock_client.return_value = mock_client_instance

        with patch.object(GoogleOAuthConfig, 'CLIENT_ID', 'test_client_id'):
            with patch.object(GoogleOAuthConfig, 'CLIENT_SECRET', 'test_client_secret'):
                with patch.object(GoogleOAuthUtils, 'verify_access_token') as mock_verify:
                    mock_verify.return_value = {
                        'user_id': mock_google_user_info['id'],
                        'email': mock_google_user_info['email'],
                        'name': mock_google_user_info['name']
                    }

                    result = await GoogleOAuthUtils.exchange_code_for_tokens(
                        'fake_auth_code', 'http://localhost/callback'
                    )

        assert result['access_token'] == mock_token_exchange_response['access_token']
        assert result['refresh_token'] == mock_token_exchange_response['refresh_token']
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