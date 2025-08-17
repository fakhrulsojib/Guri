from datetime import datetime, timezone
from typing import Dict, Any, List

# Test Log Source Data Fixtures
def get_test_log_source_base() -> Dict[str, Any]:
    """Base log source data for testing"""
    return {
        "name": "test-web-app",
        "description": "Test web application for development",
        "source_type": "application",
        "environment": "development",
        "tags": ["frontend", "react", "test"]
    }

def get_test_log_source_create() -> Dict[str, Any]:
    """LogSourceCreate model test data"""
    return get_test_log_source_base()

def get_test_log_source_in_db() -> Dict[str, Any]:
    """LogSourceInDB model test data"""
    base_data = get_test_log_source_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 1,
        "user_id": 1,
        "api_key": "test_api_key_123456789",
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "last_log_at": None,
        "log_count": 0
    })
    return base_data

def get_test_log_source_response() -> Dict[str, Any]:
    """LogSourceResponse model test data (without api_key)"""
    base_data = get_test_log_source_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 1,
        "user_id": 1,
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "last_log_at": None,
        "log_count": 0
    })
    return base_data

def get_test_log_source_response_with_key() -> Dict[str, Any]:
    """LogSourceResponseWithKey model test data (with api_key)"""
    base_data = get_test_log_source_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 1,
        "user_id": 1,
        "api_key": "test_api_key_123456789",
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "last_log_at": None,
        "log_count": 0
    })
    return base_data

def get_test_log_source_update() -> Dict[str, Any]:
    """LogSourceUpdate model test data"""
    return {
        "name": "updated-web-app",
        "description": "Updated web application description",
        "source_type": "application",
        "environment": "production",
        "tags": ["mobile", "ios", "production"],
        "status": "inactive"
    }

# Alternative log sources for different scenarios
def get_test_log_source_2() -> Dict[str, Any]:
    """Second test log source for testing multiple sources"""
    base_data = get_test_log_source_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 2,
        "name": "test-api-service",
        "description": "Test API service for backend",
        "source_type": "system",
        "environment": "staging",
        "tags": ["backend", "api", "staging"],
        "user_id": 1,
        "api_key": "test_api_key_987654321",
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "last_log_at": now,
        "log_count": 150
    })
    return base_data

def get_test_log_source_3() -> Dict[str, Any]:
    """Third test log source for testing different user ownership"""
    base_data = get_test_log_source_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 3,
        "name": "test-database",
        "description": "Test database logs",
        "source_type": "system",
        "environment": "development",
        "tags": ["database", "postgres", "dev"],
        "user_id": 2,  # Different user
        "api_key": "test_api_key_555666777",
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "last_log_at": None,
        "log_count": 0
    })
    return base_data

def get_test_inactive_log_source() -> Dict[str, Any]:
    """Inactive log source for testing status scenarios"""
    base_data = get_test_log_source_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 4,
        "name": "inactive-service",
        "description": "Inactive service for testing",
        "source_type": "custom",
        "environment": "testing",
        "tags": ["microservice", "testing", "inactive"],
        "user_id": 1,
        "api_key": "test_api_key_inactive_123",
        "status": "inactive",
        "created_at": now,
        "updated_at": now,
        "last_log_at": None,
        "log_count": 0
    })
    return base_data

def get_test_suspended_log_source() -> Dict[str, Any]:
    """Suspended log source for testing status scenarios"""
    base_data = get_test_log_source_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 5,
        "name": "suspended-service",
        "description": "Suspended service for testing",
        "source_type": "performance",
        "environment": "production",
        "tags": ["infrastructure", "monitoring", "suspended"],
        "user_id": 1,
        "api_key": "test_api_key_suspended_456",
        "status": "suspended",
        "created_at": now,
        "updated_at": now,
        "last_log_at": now,
        "log_count": 500
    })
    return base_data

# Minimal log source for testing required fields only
def get_test_minimal_log_source() -> Dict[str, Any]:
    """Minimal log source with only required fields"""
    return {
        "name": "minimal-source",
        "source_type": "custom",
        "environment": "development"
    }

# Log source with all optional fields
def get_test_comprehensive_log_source() -> Dict[str, Any]:
    """Comprehensive log source with all fields populated"""
    base_data = get_test_log_source_base()
    now = "2024-01-15T10:30:00Z"
    base_data.update({
        "id": 6,
        "name": "comprehensive-service",
        "description": "A comprehensive service with all fields populated for thorough testing",
        "source_type": "application",
        "environment": "production",
        "tags": ["web", "production", "comprehensive", "testing", "full-featured"],
        "user_id": 1,
        "api_key": "test_api_key_comprehensive_789",
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "last_log_at": now,
        "log_count": 1000
    })
    return base_data 