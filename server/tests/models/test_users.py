import os
from datetime import datetime, timezone
from typing import Dict, Any

GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Test User Data Fixtures
def get_test_user_base() -> Dict[str, Any]:
    """Base user data for testing"""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "given_name": "Test",
        "family_name": "User",
        "picture": "https://example.com/avatar.jpg",
        "locale": "en-US",
        "hd": "example.com"
    }

def get_test_user_create() -> Dict[str, Any]:
    """UserCreate model test data"""
    base_data = get_test_user_base()
    base_data.update({
        "google_id": "google_123456789",
        "email_verified": True
    })
    return base_data

def get_test_user_in_db() -> Dict[str, Any]:
    """UserInDB model test data"""
    base_data = get_test_user_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 1,
        "google_id": "google_123456789",
        "email_verified": True,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login": now
    })
    return base_data

def get_test_user_response() -> Dict[str, Any]:
    """UserResponse model test data"""
    base_data = get_test_user_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 1,
        "email_verified": True,
        "is_active": True,
        "created_at": now,
        "last_login": now
    })
    return base_data

def get_test_user_update() -> Dict[str, Any]:
    """UserUpdate model test data"""
    return {
        "name": "Updated Test User",
        "given_name": "Updated",
        "family_name": "User",
        "last_login": "2024-01-15T11:30:00Z"
    }

def get_test_refresh_token() -> Dict[str, Any]:
    """RefreshToken model test data"""
    now = "2024-01-15T10:30:00Z"
    return {
        "token_jti": "jwt_123456789",
        "user_id": 1,
        "refresh_token": "encrypted_refresh_token_123",
        "expires_at": "2024-01-16T10:30:00Z",
        "created_at": now,
        "is_revoked": False
    }

def get_test_token_response() -> Dict[str, Any]:
    """TokenResponse model test data"""
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 3600
    }

def get_test_google_auth_request() -> Dict[str, Any]:
    """GoogleAuthRequest model test data"""
    return {
        "id_token": "google_id_token_123",
        "access_token": "google_access_token_456",
        "authorization_code": "auth_code_789",
        "redirect_uri": GOOGLE_REDIRECT_URI
    }

# Alternative test users for different scenarios
def get_test_user_2() -> Dict[str, Any]:
    """Second test user for testing multiple users"""
    base_data = get_test_user_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 2,
        "email": "test2@example.com",
        "name": "Test User 2",
        "google_id": "google_987654321",
        "email_verified": True,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_login": None
    })
    return base_data

def get_test_inactive_user() -> Dict[str, Any]:
    """Inactive user for testing deactivation scenarios"""
    base_data = get_test_user_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 3,
        "email": "inactive@example.com",
        "name": "Inactive User",
        "google_id": "google_inactive_123",
        "email_verified": False,
        "is_active": False,
        "created_at": now,
        "updated_at": now,
        "last_login": None
    })
    return base_data 