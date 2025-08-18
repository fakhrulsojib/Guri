import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Import all test model fixtures
from tests.models.test_users import (
    get_test_user_create,
    get_test_user_in_db,
    get_test_user_response,
    get_test_user_update,
    get_test_refresh_token,
    get_test_token_response,
    get_test_google_auth_request,
    get_test_user_2,
    get_test_inactive_user
)

from tests.models.test_log_sources import (
    get_test_log_source_create,
    get_test_log_source_in_db,
    get_test_log_source_response,
    get_test_log_source_response_with_key,
    get_test_log_source_update,
    get_test_log_source_2,
    get_test_log_source_3,
    get_test_inactive_log_source,
    get_test_minimal_log_source
)

from tests.models.test_raw_logs import (
    get_test_raw_log_minimal,
    get_test_raw_log_with_source_id,
    get_test_raw_log_debug,
    get_test_raw_log_error,
    get_test_raw_log_critical
)

# FastAPI Test Client Fixture
@pytest.fixture
def client():
    """FastAPI test client fixture with CSRF middleware disabled for tests"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from middleware.logging_middleware import LoggingMiddleware
    from routers.health_router import health_router
    from routers.log_router import log_router
    from routers.auth_router import auth_router
    from routers.log_sources_router import router as log_sources_router
    
    test_app = FastAPI()
    
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    test_app.add_middleware(LoggingMiddleware)
    
    test_app.include_router(health_router)
    test_app.include_router(log_router)
    test_app.include_router(auth_router)
    test_app.include_router(log_sources_router)
    
    return TestClient(test_app)

# User Fixtures
@pytest.fixture
def mock_user():
    """Mock user data fixture"""
    return get_test_user_in_db()

@pytest.fixture
def mock_user_create():
    """Mock user creation data fixture"""
    return get_test_user_create()

@pytest.fixture
def mock_user_response():
    """Mock user response data fixture"""
    return get_test_user_response()

@pytest.fixture
def mock_user_update():
    """Mock user update data fixture"""
    return get_test_user_update()

@pytest.fixture
def mock_user_2():
    """Second mock user fixture"""
    return get_test_user_2()

@pytest.fixture
def mock_inactive_user():
    """Inactive user fixture"""
    return get_test_inactive_user()

@pytest.fixture
def mock_refresh_token():
    """Mock refresh token fixture"""
    return get_test_refresh_token()

@pytest.fixture
def mock_token_response():
    """Mock token response fixture"""
    return get_test_token_response()

@pytest.fixture
def mock_google_auth_request():
    """Mock Google auth request fixture"""
    return get_test_google_auth_request()

# Log Source Fixtures
@pytest.fixture
def mock_log_source():
    """Mock log source data fixture"""
    return get_test_log_source_in_db()

@pytest.fixture
def mock_log_source_create():
    """Mock log source creation data fixture"""
    return get_test_log_source_create()

@pytest.fixture
def mock_log_source_response():
    """Mock log source response data fixture"""
    return get_test_log_source_response()

@pytest.fixture
def mock_log_source_response_with_key():
    """Mock log source response with API key fixture"""
    return get_test_log_source_response_with_key()

@pytest.fixture
def mock_log_source_update():
    """Mock log source update data fixture"""
    return get_test_log_source_update()

@pytest.fixture
def mock_log_source_2():
    """Second mock log source fixture"""
    return get_test_log_source_2()

@pytest.fixture
def mock_log_source_3():
    """Third mock log source fixture (different user)"""
    return get_test_log_source_3()

@pytest.fixture
def mock_inactive_log_source():
    """Inactive log source fixture"""
    return get_test_inactive_log_source()

@pytest.fixture
def mock_minimal_log_source():
    """Minimal log source fixture"""
    return get_test_minimal_log_source()

# Raw Log Fixtures
@pytest.fixture
def mock_raw_log():
    """Mock raw log data fixture"""
    return get_test_raw_log_minimal()

@pytest.fixture
def mock_raw_log_minimal():
    """Minimal raw log fixture"""
    return get_test_raw_log_minimal()

@pytest.fixture
def mock_raw_log_with_source_id():
    """Raw log with source_id fixture"""
    return get_test_raw_log_with_source_id()

@pytest.fixture
def mock_raw_log_debug():
    """Debug level raw log fixture"""
    return get_test_raw_log_debug()

@pytest.fixture
def mock_raw_log_error():
    """Error level raw log fixture"""
    return get_test_raw_log_error()

@pytest.fixture
def mock_raw_log_critical():
    """Critical level raw log fixture"""
    return get_test_raw_log_critical()

# Collection Fixtures
@pytest.fixture
def mock_log_sources_list():
    """List of mock log sources fixture"""
    return [
        get_test_log_source_in_db(),
        get_test_log_source_2(),
        get_test_log_source_3()
    ]

@pytest.fixture
def mock_users_list():
    """List of mock users fixture"""
    return [
        get_test_user_in_db(),
        get_test_user_2(),
        get_test_inactive_user()
    ]

@pytest.fixture
def mock_raw_logs_list():
    """List of mock raw logs fixture"""
    return [
        get_test_raw_log_minimal(),
        get_test_raw_log_debug(),
        get_test_raw_log_error(),
        get_test_raw_log_critical()
    ]

# Database Result Fixtures (for CRUD testing)
@pytest.fixture
def mock_log_source_db_result():
    """Mock database result for log source (as returned by CRUD operations)"""
    return get_test_log_source_in_db()

@pytest.fixture
def mock_user_db_result():
    """Mock database result for user (as returned by CRUD operations)"""
    return get_test_user_in_db()

@pytest.fixture
def mock_log_sources_db_results():
    """Mock database results for multiple log sources"""
    return [
        get_test_log_source_in_db(),
        get_test_log_source_2(),
        get_test_log_source_3()
    ]

@pytest.fixture
def mock_users_db_results():
    """Mock database results for multiple users"""
    return [
        get_test_user_in_db(),
        get_test_user_2()
    ]

@pytest.fixture(autouse=True)
def _maybe_disable_csrf_middleware_for_tests(request):
	if request.node.get_closest_marker("enable_csrf"):
		yield
		return
	async def _bypass_csrf(self, request, call_next):
		return await call_next(request)
	with patch('middleware.csrf_middleware.CSRFMiddleware.dispatch', new=_bypass_csrf):
		yield
