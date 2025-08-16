import pytest
from util.jwt_utils import JWTUtils, JWTConfig

class TestJWTFunctions:
    def test_create_access_token(self):
        data = {"sub": "123", "email": "test@example.com"}
        token = JWTUtils.create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
    
    def test_create_refresh_token(self):
        data = {"sub": "123", "email": "test@example.com"}
        token, jti, expires_at = JWTUtils.create_refresh_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert jti is not None
        assert expires_at is not None
    
    def test_create_token_pair(self):
        token_data = JWTUtils.create_token_pair("123", "test@example.com")
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert "token_type" in token_data
        assert "jti" in token_data
        assert "expires_at" in token_data
        assert token_data["token_type"] == "bearer"
    
    def test_verify_valid_token(self):
        data = {"sub": "123", "email": "test@example.com"}
        token = JWTUtils.create_access_token(data)
        payload = JWTUtils.verify_token(token)
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
    
    def test_verify_invalid_token(self):
        with pytest.raises(Exception):
            JWTUtils.verify_token("invalid_token") 