from unittest.mock import patch
from fastapi import HTTPException
import pytest
from services.log_source_service import LogSourceService
from model.log_sources import LogSourceCreate, LogSourceUpdate, LogSourceInDB, LogSourceStatus, LogSourceType

SERVICE_MODULE = 'services.log_source_service'

class TestLogSourceService:
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.create_log_source')
    @patch(f'{SERVICE_MODULE}.LogSourceService.get_log_source')
    def test_create_log_source_success(self, mock_get_source, mock_create, mock_check_name, mock_log_source_create, mock_log_source_db_result):
        """Test successful log source creation"""
        mock_check_name.return_value = True
        mock_create.return_value = {"id": 1}
        
        mock_created_source = LogSourceInDB(**mock_log_source_db_result)
        mock_get_source.return_value = mock_created_source
        
        result = LogSourceService.create_log_source(LogSourceCreate(**mock_log_source_create), user_id=1)
        
        assert result is not None
        assert result.id == 1
        assert result.name == mock_log_source_create["name"]
        mock_check_name.assert_called_once_with(mock_log_source_create["name"], 1, None)
        mock_create.assert_called_once()
        mock_get_source.assert_called_once_with(1, 1)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    def test_create_log_source_name_conflict(self, mock_check_name, mock_log_source_create):
        """Test log source creation with duplicate name"""
        mock_check_name.return_value = False
        
        with patch(f'{SERVICE_MODULE}.LogSourceCRUD.create_log_source'):
            with patch(f'{SERVICE_MODULE}.LogSourceService.get_log_source'):
                with pytest.raises(HTTPException) as exc_info:
                    LogSourceService.create_log_source(LogSourceCreate(**mock_log_source_create), user_id=1)
                
                assert exc_info.value.status_code == 409
                assert "Log source name already exists" in str(exc_info.value.detail)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.create_log_source')
    def test_create_log_source_db_failure(self, mock_create, mock_check_name, mock_log_source_create):
        """Test log source creation when database operation fails"""
        mock_check_name.return_value = True
        mock_create.return_value = None
        
        with patch(f'{SERVICE_MODULE}.LogSourceService.get_log_source'):
            with pytest.raises(HTTPException) as exc_info:
                LogSourceService.create_log_source(LogSourceCreate(**mock_log_source_create), user_id=1)
            
            assert exc_info.value.status_code == 500
            assert "Failed to create log source" in str(exc_info.value.detail)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_user_log_sources')
    def test_get_user_log_sources_success(self, mock_get_sources, mock_log_sources_db_results):
        """Test successful retrieval of user log sources"""
        mock_get_sources.return_value = mock_log_sources_db_results
        
        results = LogSourceService.get_user_log_sources(user_id=1)
        
        assert len(results) == 3
        assert results[0].id == 1
        assert results[0].name == mock_log_sources_db_results[0]["name"]
        mock_get_sources.assert_called_once_with(1, None, None)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_user_log_sources')
    def test_get_user_log_sources_with_filters(self, mock_get_sources, mock_log_sources_db_results):
        """Test retrieval of user log sources with status and environment filters"""
        mock_get_sources.return_value = mock_log_sources_db_results
        
        results = LogSourceService.get_user_log_sources(
            user_id=1, 
            status=LogSourceStatus.ACTIVE.value, 
            environment="development"
        )
        
        assert len(results) == 3
        mock_get_sources.assert_called_once_with(1, LogSourceStatus.ACTIVE.value, "development")
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_user_log_sources')
    def test_get_user_log_sources_empty(self, mock_get_sources):
        """Test retrieval of user log sources when none exist"""
        mock_get_sources.return_value = []
        
        results = LogSourceService.get_user_log_sources(user_id=1)
        
        assert len(results) == 0
        mock_get_sources.assert_called_once_with(1, None, None)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_log_source_by_id')
    def test_get_log_source_success(self, mock_get_source, mock_log_source_db_result):
        """Test successful retrieval of log source by ID"""
        mock_get_source.return_value = mock_log_source_db_result
        
        result = LogSourceService.get_log_source(1, 1)
        
        assert result is not None
        assert result.id == 1
        assert result.name == mock_log_source_db_result["name"]
        mock_get_source.assert_called_once_with(1, 1)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_log_source_by_id')
    def test_get_log_source_not_found(self, mock_get_source):
        """Test retrieval of non-existent log source"""
        mock_get_source.return_value = None
        
        result = LogSourceService.get_log_source(999, 1)
        
        assert result is None
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_log_source_by_api_key')
    def test_get_log_source_by_api_key_success(self, mock_get_source, mock_log_source_db_result):
        """Test successful retrieval of log source by API key"""
        mock_get_source.return_value = mock_log_source_db_result
        
        result = LogSourceService.get_log_source_by_api_key("test_api_key_123456789")
        
        assert result is not None
        assert result.id == 1
        assert result.api_key == "test_api_key_123456789"
        mock_get_source.assert_called_once_with("test_api_key_123456789")
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_log_source_by_api_key')
    def test_get_log_source_by_api_key_not_found(self, mock_get_source):
        """Test retrieval of log source by non-existent API key"""
        mock_get_source.return_value = None
        
        result = LogSourceService.get_log_source_by_api_key("non_existent_key")
        
        assert result is None
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.update_log_source')
    @patch(f'{SERVICE_MODULE}.LogSourceService.get_log_source')
    def test_update_log_source_success(self, mock_get_source, mock_update, mock_check_name, mock_log_source_db_result, mock_log_source_update):
        """Test successful log source update"""
        existing_source = LogSourceInDB(**mock_log_source_db_result)
        mock_get_source.return_value = existing_source
        mock_check_name.return_value = True
        mock_update.return_value = True
        
        update_data = LogSourceUpdate(**mock_log_source_update)
        result = LogSourceService.update_log_source(1, 1, update_data)
        
        assert result is not None
        mock_check_name.assert_called_once_with(mock_log_source_update["name"], 1, 1)
        mock_update.assert_called_once()
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_log_source_by_id')
    def test_update_log_source_not_found(self, mock_get_source, mock_log_source_update):
        """Test update of non-existent log source"""
        mock_get_source.return_value = None
        
        result = LogSourceService.update_log_source(999, 1, LogSourceUpdate(**mock_log_source_update))
        
        assert result is None
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    @patch(f'{SERVICE_MODULE}.LogSourceService.get_log_source')
    def test_update_log_source_name_conflict(self, mock_get_source, mock_check_name, mock_log_source_db_result, mock_log_source_update):
        """Test log source update with duplicate name"""
        existing_source = LogSourceInDB(**mock_log_source_db_result)
        mock_get_source.return_value = existing_source
        mock_check_name.return_value = False
        
        with patch(f'{SERVICE_MODULE}.LogSourceCRUD.update_log_source'):
            with pytest.raises(HTTPException) as exc_info:
                LogSourceService.update_log_source(1, 1, LogSourceUpdate(**mock_log_source_update))
            
            assert exc_info.value.status_code == 409
            assert "Log source name already exists" in str(exc_info.value.detail)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.update_log_source')
    @patch(f'{SERVICE_MODULE}.LogSourceService.get_log_source')
    def test_update_log_source_no_changes(self, mock_get_source, mock_update, mock_check_name, mock_log_source_db_result):
        """Test log source update with no changes"""
        existing_source = LogSourceInDB(**mock_log_source_db_result)
        mock_get_source.return_value = existing_source
        mock_check_name.return_value = True
        mock_update.return_value = True
        
        update_data = LogSourceUpdate()  # Empty update
        result = LogSourceService.update_log_source(1, 1, update_data)
        
        assert result is not None
        mock_update.assert_not_called()
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.update_log_source')
    @patch(f'{SERVICE_MODULE}.LogSourceService.get_log_source')
    def test_update_log_source_partial_fields(self, mock_get_source, mock_update, mock_check_name, mock_log_source_db_result):
        """Test log source update with partial fields"""
        existing_source = LogSourceInDB(**mock_log_source_db_result)
        mock_get_source.return_value = existing_source
        mock_check_name.return_value = True
        mock_update.return_value = True
        
        update_data = LogSourceUpdate(
            name="updated-name",
            environment="production"
        )
        result = LogSourceService.update_log_source(1, 1, update_data)
        
        assert result is not None
        mock_update.assert_called_once()
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.delete_log_source')
    @patch(f'{SERVICE_MODULE}.LogSourceService.get_log_source')
    def test_delete_log_source_success(self, mock_get_source, mock_delete, mock_log_source_db_result):
        """Test successful log source deletion"""
        existing_source = LogSourceInDB(**mock_log_source_db_result)
        mock_get_source.return_value = existing_source
        mock_delete.return_value = True
        
        result = LogSourceService.delete_log_source(1, 1)
        
        assert result is True
        mock_delete.assert_called_once_with(1, 1)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.get_log_source_by_id')
    def test_delete_log_source_not_found(self, mock_get_source):
        """Test deletion of non-existent log source"""
        mock_get_source.return_value = None
        
        result = LogSourceService.delete_log_source(999, 1)
        
        assert result is False
    
    @patch(f'{SERVICE_MODULE}.LogSourceService._generate_api_key')
    def test_generate_api_key(self, mock_generate):
        """Test API key generation"""
        mock_generate.return_value = "generated_key_123"
        
        result = LogSourceService._generate_api_key()
        
        assert result == "generated_key_123"
        mock_generate.assert_called_once()
    
    @patch(f'{SERVICE_MODULE}.LogSourceService._generate_api_key')
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_api_key_uniqueness')
    def test_ensure_unique_api_key_success(self, mock_check, mock_generate):
        """Test successful API key uniqueness check"""
        mock_generate.return_value = "unique_key_123"
        mock_check.return_value = True
        
        result = LogSourceService._ensure_unique_api_key()
        
        assert result == "unique_key_123"
        mock_generate.assert_called_once()
        mock_check.assert_called_once_with("unique_key_123")
    
    @patch(f'{SERVICE_MODULE}.LogSourceService._generate_api_key')
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_api_key_uniqueness')
    def test_ensure_unique_api_key_max_attempts(self, mock_check, mock_generate):
        """Test API key uniqueness check with max attempts"""
        mock_generate.side_effect = ["key1", "key2", "key3", "key4", "key5", "key6", "key7", "key8", "key9", "key10", "key11"]
        mock_check.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            LogSourceService._ensure_unique_api_key()
        
        assert exc_info.value.status_code == 500
        assert "Failed to generate unique API key" in str(exc_info.value.detail)
        assert mock_generate.call_count == 10
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    def test_check_name_uniqueness_success(self, mock_check):
        """Test successful name uniqueness check"""
        mock_check.return_value = True
        
        LogSourceService._check_name_uniqueness("unique_name", 1)
        
        mock_check.assert_called_once_with("unique_name", 1, None)
    
    @patch(f'{SERVICE_MODULE}.LogSourceCRUD.check_name_uniqueness')
    def test_check_name_uniqueness_conflict(self, mock_check):
        """Test name uniqueness check with conflict"""
        mock_check.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            LogSourceService._check_name_uniqueness("existing_name", 1)
        
        assert exc_info.value.status_code == 409
        assert "Log source name already exists" in str(exc_info.value.detail)
        mock_check.assert_called_once_with("existing_name", 1, None) 