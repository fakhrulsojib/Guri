import secrets
import string
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from database.LogSourceCrud import LogSourceCRUD
from model.log_sources import LogSourceCreate, LogSourceUpdate, LogSourceInDB, LogSourceResponse, LogSourceStatus

class LogSourceService:
    @staticmethod
    def _generate_api_key() -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @staticmethod
    def _ensure_unique_api_key() -> str:
        max_attempts = 10
        for _ in range(max_attempts):
            api_key = LogSourceService._generate_api_key()
            if LogSourceCRUD.check_api_key_uniqueness(api_key):
                return api_key
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate unique API key"
        )
    
    @staticmethod
    def _check_name_uniqueness(name: str, user_id: int, exclude_id: Optional[int] = None) -> None:
        if not LogSourceCRUD.check_name_uniqueness(name, user_id, exclude_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Log source name already exists for this user"
            )
    
    @staticmethod
    def create_log_source(log_source_data: LogSourceCreate, user_id: int) -> LogSourceInDB:
        LogSourceService._check_name_uniqueness(log_source_data.name, user_id)
        
        api_key = LogSourceService._ensure_unique_api_key()
        now = datetime.now(timezone.utc)
        
        result = LogSourceCRUD.create_log_source(
            user_id=user_id,
            name=log_source_data.name,
            description=log_source_data.description,
            source_type=log_source_data.source_type.value,
            environment=log_source_data.environment,
            tags=log_source_data.tags,
            api_key=api_key,
            status=LogSourceStatus.ACTIVE.value,
            created_at=now,
            updated_at=now
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create log source"
            )
        
        return LogSourceService.get_log_source(result["id"], user_id)
    
    @staticmethod
    def get_user_log_sources(user_id: int, status: Optional[str] = None, environment: Optional[str] = None) -> List[LogSourceInDB]:
        results = LogSourceCRUD.get_user_log_sources(user_id, status, environment)
        return [LogSourceInDB(**result) for result in results]
    
    @staticmethod
    def get_log_source(log_source_id: int, user_id: int) -> Optional[LogSourceInDB]:
        result = LogSourceCRUD.get_log_source_by_id(log_source_id, user_id)
        
        if not result:
            return None
        
        return LogSourceInDB(**result)
    
    @staticmethod
    def get_log_source_by_api_key(api_key: str) -> Optional[LogSourceInDB]:
        result = LogSourceCRUD.get_log_source_by_api_key(api_key)
        
        if not result:
            return None
        
        return LogSourceInDB(**result)
    
    @staticmethod
    def update_log_source(log_source_id: int, user_id: int, update_data: LogSourceUpdate) -> Optional[LogSourceInDB]:
        log_source = LogSourceService.get_log_source(log_source_id, user_id)
        if not log_source:
            return None
        
        if update_data.name and update_data.name != log_source.name:
            LogSourceService._check_name_uniqueness(update_data.name, user_id, log_source_id)
        
        update_fields = []
        params = []
        
        if update_data.name is not None:
            update_fields.append("name = %s")
            params.append(update_data.name)
        
        if update_data.description is not None:
            update_fields.append("description = %s")
            params.append(update_data.description)
        
        if update_data.source_type is not None:
            update_fields.append("source_type = %s")
            params.append(update_data.source_type.value)
        
        if update_data.environment is not None:
            update_fields.append("environment = %s")
            params.append(update_data.environment)
        
        if update_data.tags is not None:
            update_fields.append("tags = %s")
            params.append(update_data.tags)
        
        if update_data.status is not None:
            update_fields.append("status = %s")
            params.append(update_data.status.value)
        
        if not update_fields:
            return log_source
        
        LogSourceCRUD.update_log_source(log_source_id, user_id, update_fields, params)
        
        return LogSourceService.get_log_source(log_source_id, user_id)
    
    @staticmethod
    def delete_log_source(log_source_id: int, user_id: int) -> bool:
        log_source = LogSourceService.get_log_source(log_source_id, user_id)
        if not log_source:
            return False
        
        return LogSourceCRUD.delete_log_source(log_source_id, user_id) 