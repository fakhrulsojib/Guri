from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app
from model.log_sources import LogSourceType, LogSourceStatus, LogSourceInDB
from services.auth_service import get_current_user
from routers.log_sources_router import security
from fastapi import HTTPException, status

def mock_get_current_user():
    return {
        "id": 1,
        "email": "test@example.com",
        "google_id": "google123",
        "name": "Test User",
        "is_active": True
    }

def mock_security():
    return "mock_token"

class TestLogSourcesRouter:
    """Phase 1: Core Functionality Tests for Log Sources Router"""
    
    def setup_method(self):
        """Set up test dependencies before each test"""
        app.dependency_overrides[get_current_user] = mock_get_current_user
        app.dependency_overrides[security] = mock_security
    
    def teardown_method(self):
        """Clean up test dependencies after each test"""
        app.dependency_overrides.clear()
    
    @patch('routers.log_sources_router.LogSourceService.create_log_source')
    def test_create_log_source_valid_creation(self, mock_create_service, mock_log_source_create, mock_log_source_db_result):
        """Test valid log source creation with all required fields"""
        mock_log_source = LogSourceInDB(**mock_log_source_db_result)
        mock_create_service.return_value = mock_log_source
        
        client = TestClient(app)
        response = client.post("/api/v1/log-sources", json=mock_log_source_create)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == mock_log_source_create["name"]
        assert data["source_type"] == mock_log_source_create["source_type"]
        assert data["environment"] == mock_log_source_create["environment"]
        assert "id" in data
        assert "api_key" in data  # API key should be returned on creation
        assert data["api_key"] == mock_log_source_db_result["api_key"]
    
    @patch('routers.log_sources_router.LogSourceService.create_log_source')
    def test_create_log_source_minimal_data(self, mock_create_service, mock_minimal_log_source, mock_log_source_db_result):
        """Test log source creation with only required fields"""
        # Create a minimal log source object
        minimal_source_data = mock_log_source_db_result.copy()
        minimal_source_data.update({
            "name": mock_minimal_log_source["name"],
            "description": None,
            "source_type": mock_minimal_log_source["source_type"],
            "environment": mock_minimal_log_source["environment"],
            "tags": []
        })
        
        minimal_source = LogSourceInDB(**minimal_source_data)
        mock_create_service.return_value = minimal_source
        
        client = TestClient(app)
        response = client.post("/api/v1/log-sources", json=mock_minimal_log_source)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == mock_minimal_log_source["name"]
        assert data["description"] is None
        assert data["tags"] == []
        assert "api_key" in data
    
    def test_create_log_source_missing_required_fields(self):
        """Test creation with missing required fields"""
        client = TestClient(app)
        incomplete_data = {"name": "test-app"}
        
        response = client.post("/api/v1/log-sources", json=incomplete_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_log_source_invalid_source_type(self, mock_log_source_create):
        """Test creation with invalid source_type enum value"""
        client = TestClient(app)
        invalid_data = mock_log_source_create.copy()
        invalid_data["source_type"] = "invalid_type"
        
        response = client.post("/api/v1/log-sources", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_log_source_name_too_long(self, mock_log_source_create):
        """Test creation with name exceeding 100 characters"""
        client = TestClient(app)
        invalid_data = mock_log_source_create.copy()
        invalid_data["name"] = "a" * 101
        
        response = client.post("/api/v1/log-sources", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_log_source_description_too_long(self, mock_log_source_create):
        """Test creation with description exceeding 500 characters"""
        client = TestClient(app)
        invalid_data = mock_log_source_create.copy()
        invalid_data["description"] = "a" * 501
        
        response = client.post("/api/v1/log-sources", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_create_log_source_unauthorized_no_token(self, mock_log_source_create):
        """Test creation without authentication token"""
        app.dependency_overrides.clear()
        client = TestClient(app)
        
        response = client.post("/api/v1/log-sources", json=mock_log_source_create)
        
        assert response.status_code == 403
    
    def test_create_log_source_invalid_token(self, mock_log_source_create):
        """Test creation with invalid authentication token"""
        def mock_invalid_user():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        app.dependency_overrides[get_current_user] = mock_invalid_user
        client = TestClient(app)
        
        response = client.post("/api/v1/log-sources", json=mock_log_source_create)
        
        assert response.status_code == 401
    
    @patch('routers.log_sources_router.LogSourceService.get_user_log_sources')
    def test_get_all_log_sources_authenticated(self, mock_get_sources, mock_log_source_db_result):
        """Test authenticated request returns only current user's sources"""
        mock_log_source = LogSourceInDB(**mock_log_source_db_result)
        
        mock_get_sources.return_value = [mock_log_source]
        
        client = TestClient(app)
        response = client.get("/api/v1/log-sources")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["user_id"] == mock_log_source.user_id
    
    @patch('routers.log_sources_router.LogSourceService.get_user_log_sources')
    def test_get_all_log_sources_empty_list(self, mock_get_sources):
        """Test returns empty list when user has no log sources"""
        mock_get_sources.return_value = []
        
        client = TestClient(app)
        response = client.get("/api/v1/log-sources")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    @patch('routers.log_sources_router.LogSourceService.get_user_log_sources')
    def test_get_all_log_sources_with_filters(self, mock_get_sources, mock_log_source_db_result):
        """Test filtering log sources by status and environment"""
        mock_log_source = LogSourceInDB(**mock_log_source_db_result)
        
        mock_get_sources.return_value = [mock_log_source]
        
        client = TestClient(app)
        response = client.get("/api/v1/log-sources?status=active&environment=dev")
        
        assert response.status_code == 200
        mock_get_sources.assert_called_once()
    
    def test_get_all_log_sources_unauthorized(self):
        """Test getting log sources without authentication"""
        app.dependency_overrides.clear()
        client = TestClient(app)
        
        response = client.get("/api/v1/log-sources")
        
        assert response.status_code == 403
    
    @patch('routers.log_sources_router.LogSourceService.get_log_source')
    def test_get_single_log_source_valid_id(self, mock_get_source, mock_log_source_db_result):
        """Test getting log source with valid ID for current user"""
        mock_log_source = LogSourceInDB(**mock_log_source_db_result)
        
        mock_get_source.return_value = mock_log_source
        
        client = TestClient(app)
        response = client.get("/api/v1/log-sources/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == mock_log_source.name
    
    @patch('routers.log_sources_router.LogSourceService.get_log_source')
    def test_get_single_log_source_nonexistent_id(self, mock_get_source):
        """Test getting log source with non-existent ID"""
        mock_get_source.return_value = None
        
        client = TestClient(app)
        response = client.get("/api/v1/log-sources/999")
        
        assert response.status_code == 404
    
    @patch('routers.log_sources_router.LogSourceService.get_log_source')
    def test_get_single_log_source_belongs_to_another_user(self, mock_get_source):
        """Test getting log source that belongs to another user"""
        mock_get_source.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
        
        client = TestClient(app)
        response = client.get("/api/v1/log-sources/2")
        
        assert response.status_code == 403
    
    def test_get_single_log_source_invalid_id_format(self):
        """Test getting log source with invalid ID format"""
        client = TestClient(app)
        response = client.get("/api/v1/log-sources/invalid")
        
        assert response.status_code == 422
    
    def test_get_single_log_source_unauthorized(self):
        """Test getting log source without authentication"""
        app.dependency_overrides.clear()
        client = TestClient(app)
        
        response = client.get("/api/v1/log-sources/1")
        
        assert response.status_code == 403
    
    @patch('routers.log_sources_router.LogSourceService.update_log_source')
    def test_update_log_source_partial_update(self, mock_update_service, mock_log_source_db_result):
        """Test partial update changes only specified fields"""
        updated_source = LogSourceInDB(**mock_log_source_db_result)
        updated_source.name = "updated-name"
        updated_source.updated_at = updated_source.updated_at.replace(minute=31) # Simulate partial update
        
        mock_update_service.return_value = updated_source
        
        client = TestClient(app)
        update_data = {"name": "updated-name"}
        response = client.patch("/api/v1/log-sources/1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated-name"
        assert data["description"] == mock_log_source_db_result["description"]
    
    @patch('routers.log_sources_router.LogSourceService.update_log_source')
    def test_update_log_source_status_change(self, mock_update_service, mock_log_source_db_result):
        """Test updating log source status"""
        updated_source = LogSourceInDB(**mock_log_source_db_result)
        updated_source.status = LogSourceStatus.INACTIVE
        updated_source.updated_at = updated_source.updated_at.replace(minute=30) # Simulate status change
        
        mock_update_service.return_value = updated_source
        
        client = TestClient(app)
        update_data = {"status": "inactive"}
        response = client.patch("/api/v1/log-sources/1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"
    
    def test_update_log_source_invalid_status(self):
        """Test updating with invalid status enum value"""
        client = TestClient(app)
        update_data = {"status": "invalid_status"}
        
        response = client.patch("/api/v1/log-sources/1", json=update_data)
        
        assert response.status_code == 422
    
    def test_update_log_source_invalid_tags(self):
        """Test updating with invalid tags format"""
        client = TestClient(app)
        update_data = {"tags": "not_a_list"}
        
        response = client.patch("/api/v1/log-sources/1", json=update_data)
        
        assert response.status_code == 422
    
    @patch('routers.log_sources_router.LogSourceService.update_log_source')
    def test_update_log_source_nonexistent_id(self, mock_update_service):
        """Test updating non-existent log source"""
        mock_update_service.return_value = None
        
        client = TestClient(app)
        response = client.patch("/api/v1/log-sources/1", json={"name": "new-name"})
        
        assert response.status_code == 404
    
    def test_update_log_source_unauthorized(self):
        """Test updating log source without authentication"""
        app.dependency_overrides.clear()
        client = TestClient(app)
        
        response = client.patch("/api/v1/log-sources/1", json={"name": "new-name"})
        
        assert response.status_code == 403
    
    @patch('routers.log_sources_router.LogSourceService.delete_log_source')
    def test_delete_log_source_valid_delete(self, mock_delete_service):
        """Test valid deletion returns 204"""
        mock_delete_service.return_value = True
        
        client = TestClient(app)
        response = client.delete("/api/v1/log-sources/1")
        
        assert response.status_code == 204
    
    @patch('routers.log_sources_router.LogSourceService.delete_log_source')
    def test_delete_log_source_nonexistent_id(self, mock_delete_service):
        """Test deleting non-existent log source"""
        mock_delete_service.return_value = False
        
        client = TestClient(app)
        response = client.delete("/api/v1/log-sources/999")
        
        assert response.status_code == 404
    
    @patch('routers.log_sources_router.LogSourceService.delete_log_source')
    def test_delete_log_source_belongs_to_another_user(self, mock_delete_service):
        """Test deleting log source that belongs to another user"""
        mock_delete_service.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
        
        client = TestClient(app)
        response = client.delete("/api/v1/log-sources/2")
        
        assert response.status_code == 403
    
    def test_delete_log_source_unauthorized(self):
        """Test deleting log source without authentication"""
        app.dependency_overrides.clear()
        client = TestClient(app)
        
        response = client.delete("/api/v1/log-sources/1")
        
        assert response.status_code == 403
    
    @patch('routers.log_sources_router.LogSourceService.get_log_source')
    def test_get_log_source_api_key_valid(self, mock_get_source, mock_log_source_db_result):
        """Test getting API key for a valid log source owned by current user"""
        mock_log_source = LogSourceInDB(**mock_log_source_db_result)
        
        mock_get_source.return_value = mock_log_source
        
        client = TestClient(app)
        response = client.get("/api/v1/log-sources/1/api-key")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"] == mock_log_source.api_key
    
    @patch('routers.log_sources_router.LogSourceService.get_log_source')
    def test_get_log_source_api_key_nonexistent(self, mock_get_source):
        """Test getting API key for non-existent log source"""
        mock_get_source.return_value = None
        
        client = TestClient(app)
        response = client.get("/api/v1/log-sources/999/api-key")
        
        assert response.status_code == 404
    
    @patch('routers.log_sources_router.LogSourceService.get_log_source')
    def test_get_log_source_api_key_unauthorized(self, mock_get_source):
        """Test getting API key without authentication"""
        app.dependency_overrides.clear()
        client = TestClient(app)
        
        response = client.get("/api/v1/log-sources/1/api-key")
        
        assert response.status_code == 403