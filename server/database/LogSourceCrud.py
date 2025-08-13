from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from .database import execute_query, execute_query_with_result, execute_query_single_result
from model.log_sources import LogSourceCreate, LogSourceUpdate, LogSourceStatus

class LogSourceCRUD:
    @staticmethod
    def create_log_source(user_id: int, name: str, description: str, source_type: str, 
                         environment: str, tags: str, api_key: str, status: str, 
                         created_at: datetime, updated_at: datetime) -> Optional[Dict[str, Any]]:
        query = """
        INSERT INTO log_sources (user_id, name, description, source_type, environment, tags, api_key, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        params = (user_id, name, description, source_type, environment, tags, api_key, status, created_at, updated_at)
        return execute_query_single_result(query, params)
    
    @staticmethod
    def get_log_source_by_id(log_source_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM log_sources WHERE id = %s AND user_id = %s"
        return execute_query_single_result(query, (log_source_id, user_id))
    
    @staticmethod
    def get_log_source_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM log_sources WHERE api_key = %s"
        return execute_query_single_result(query, (api_key,))
    
    @staticmethod
    def get_user_log_sources(user_id: int, status: Optional[str] = None, environment: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM log_sources WHERE user_id = %s"
        params = [user_id]
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if environment:
            query += " AND environment = %s"
            params.append(environment)
        
        query += " ORDER BY created_at DESC"
        return execute_query_with_result(query, tuple(params))
    
    @staticmethod
    def check_name_uniqueness(name: str, user_id: int, exclude_id: Optional[int] = None) -> bool:
        query = "SELECT id FROM log_sources WHERE name = %s AND user_id = %s"
        params = (name, user_id)
        
        if exclude_id:
            query += " AND id != %s"
            params = (name, user_id, exclude_id)
        
        result = execute_query_single_result(query, params)
        return result is None
    
    @staticmethod
    def check_api_key_uniqueness(api_key: str) -> bool:
        query = "SELECT id FROM log_sources WHERE api_key = %s"
        result = execute_query_single_result(query, (api_key,))
        return result is None
    
    @staticmethod
    def update_log_source(log_source_id: int, user_id: int, update_fields: List[str], params: List[Any]) -> bool:
        if not update_fields:
            return True
        
        update_fields.append("updated_at = %s")
        params.extend([datetime.now(timezone.utc), log_source_id, user_id])
        
        query = f"UPDATE log_sources SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
        execute_query(query, tuple(params))
        return True
    
    @staticmethod
    def delete_log_source(log_source_id: int, user_id: int) -> bool:
        query = "DELETE FROM log_sources WHERE id = %s AND user_id = %s"
        execute_query(query, (log_source_id, user_id))
        return True 