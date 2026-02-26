from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from .database import (
    async_execute_query,
    async_execute_query_with_result,
    async_execute_query_single_result,
)
from model.log_sources import LogSourceCreate, LogSourceUpdate, LogSourceStatus


class LogSourceCRUD:
    @staticmethod
    async def create_log_source(
        user_id: int,
        name: str,
        description: str,
        source_type: str,
        environment: str,
        tags: str,
        api_key: str,
        status: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> Optional[Dict[str, Any]]:
        query = """
        INSERT INTO log_sources (user_id, name, description, source_type, environment, tags, api_key, status, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        RETURNING id
        """
        params = (
            user_id, name, description, source_type,
            environment, tags, api_key, status,
            created_at, updated_at,
        )
        return await async_execute_query_single_result(query, params)

    @staticmethod
    async def get_log_source_by_id(log_source_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM log_sources WHERE id = $1 AND user_id = $2"
        return await async_execute_query_single_result(query, (log_source_id, user_id))

    @staticmethod
    async def get_log_source_by_api_key(api_key: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM log_sources WHERE api_key = $1"
        return await async_execute_query_single_result(query, (api_key,))

    @staticmethod
    async def get_user_log_sources(
        user_id: int,
        status: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM log_sources WHERE user_id = $1"
        params: list = [user_id]
        idx = 2

        if status:
            query += f" AND status = ${idx}"
            params.append(status)
            idx += 1

        if environment:
            query += f" AND environment = ${idx}"
            params.append(environment)
            idx += 1

        query += " ORDER BY created_at DESC"
        return await async_execute_query_with_result(query, tuple(params))

    @staticmethod
    async def check_name_uniqueness(
        name: str, user_id: int, exclude_id: Optional[int] = None,
    ) -> bool:
        if exclude_id:
            query = "SELECT id FROM log_sources WHERE name = $1 AND user_id = $2 AND id != $3"
            params = (name, user_id, exclude_id)
        else:
            query = "SELECT id FROM log_sources WHERE name = $1 AND user_id = $2"
            params = (name, user_id)

        result = await async_execute_query_single_result(query, params)
        return result is None

    @staticmethod
    async def check_api_key_uniqueness(api_key: str) -> bool:
        query = "SELECT id FROM log_sources WHERE api_key = $1"
        result = await async_execute_query_single_result(query, (api_key,))
        return result is None

    @staticmethod
    async def update_log_source(
        log_source_id: int,
        user_id: int,
        update_fields: List[str],
        params: List[Any],
    ) -> bool:
        if not update_fields:
            return True

        # Append updated_at field
        next_idx = len(params) + 1
        update_fields.append(f"updated_at = ${next_idx}")
        params.append(datetime.now(timezone.utc))

        # WHERE clause params
        id_idx = len(params) + 1
        uid_idx = id_idx + 1
        params.extend([log_source_id, user_id])

        query = f"UPDATE log_sources SET {', '.join(update_fields)} WHERE id = ${id_idx} AND user_id = ${uid_idx}"
        await async_execute_query(query, tuple(params))
        return True

    @staticmethod
    async def delete_log_source(log_source_id: int, user_id: int) -> bool:
        query = "DELETE FROM log_sources WHERE id = $1 AND user_id = $2"
        await async_execute_query(query, (log_source_id, user_id))
        return True