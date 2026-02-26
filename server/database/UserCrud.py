from datetime import datetime
from typing import Optional, List, Dict, Any
from .database import (
    async_execute_query,
    async_execute_query_with_result,
    async_execute_query_single_result,
)
from model.user import UserCreate, UserUpdate, UserInDB, RefreshToken


class UserCRUD:
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE id = $1"
        return await async_execute_query_single_result(query, (user_id,))

    @staticmethod
    async def get_user_by_google_id(google_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE google_id = $1"
        return await async_execute_query_single_result(query, (google_id,))

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE email = $1"
        return await async_execute_query_single_result(query, (email,))

    @staticmethod
    async def create_user(user_data: UserCreate) -> Dict[str, Any]:
        query = """
        INSERT INTO users (google_id, email, email_verified, name, given_name, family_name, picture, locale, hd)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
        """
        params = (
            user_data.google_id,
            user_data.email,
            user_data.email_verified,
            user_data.name,
            user_data.given_name,
            user_data.family_name,
            user_data.picture,
            user_data.locale,
            user_data.hd,
        )

        result = await async_execute_query_single_result(query, params)
        if not result:
            raise Exception("Failed to create user")
        return result

    @staticmethod
    async def update_user(user_id: int, user_data: UserUpdate) -> Optional[Dict[str, Any]]:
        update_fields = []
        params: list = []
        idx = 1

        if user_data.name is not None:
            update_fields.append(f"name = ${idx}")
            params.append(user_data.name)
            idx += 1
        if user_data.given_name is not None:
            update_fields.append(f"given_name = ${idx}")
            params.append(user_data.given_name)
            idx += 1
        if user_data.family_name is not None:
            update_fields.append(f"family_name = ${idx}")
            params.append(user_data.family_name)
            idx += 1
        if user_data.picture is not None:
            update_fields.append(f"picture = ${idx}")
            params.append(user_data.picture)
            idx += 1
        if user_data.locale is not None:
            update_fields.append(f"locale = ${idx}")
            params.append(user_data.locale)
            idx += 1
        if user_data.hd is not None:
            update_fields.append(f"hd = ${idx}")
            params.append(user_data.hd)
            idx += 1
        if user_data.last_login is not None:
            update_fields.append(f"last_login = ${idx}")
            params.append(user_data.last_login)
            idx += 1

        if not update_fields:
            return await UserCRUD.get_user_by_id(user_id)

        update_fields.append("updated_at = NOW()")
        params.append(user_id)

        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ${idx} RETURNING *"
        return await async_execute_query_single_result(query, tuple(params))

    @staticmethod
    async def update_last_login(user_id: int) -> Optional[Dict[str, Any]]:
        query = "UPDATE users SET last_login = NOW() WHERE id = $1 RETURNING *"
        return await async_execute_query_single_result(query, (user_id,))

    @staticmethod
    async def deactivate_user(user_id: int) -> Optional[Dict[str, Any]]:
        query = "UPDATE users SET is_active = FALSE WHERE id = $1 RETURNING *"
        return await async_execute_query_single_result(query, (user_id,))

    @staticmethod
    async def get_active_users(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at DESC LIMIT $1 OFFSET $2"
        return await async_execute_query_with_result(query, (limit, skip))

    @staticmethod
    async def user_exists_by_google_id(google_id: str) -> bool:
        result = await UserCRUD.get_user_by_google_id(google_id)
        return result is not None

    @staticmethod
    async def user_exists_by_email(email: str) -> bool:
        result = await UserCRUD.get_user_by_email(email)
        return result is not None


class RefreshTokenCRUD:
    @staticmethod
    async def store_refresh_token(
        token_jti: str, user_id: int, refresh_token: str, expires_at: datetime,
    ) -> Dict[str, Any]:
        query = """
        INSERT INTO refresh_tokens (token_jti, user_id, refresh_token, expires_at)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """
        params = (token_jti, user_id, refresh_token, expires_at)

        result = await async_execute_query_single_result(query, params)
        if not result:
            raise Exception("Failed to store refresh token")
        return result

    @staticmethod
    async def get_refresh_token(token_jti: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM refresh_tokens WHERE token_jti = $1 AND is_revoked = FALSE"
        return await async_execute_query_single_result(query, (token_jti,))

    @staticmethod
    async def revoke_refresh_token(token_jti: str) -> bool:
        query = "UPDATE refresh_tokens SET is_revoked = TRUE WHERE token_jti = $1"
        try:
            await async_execute_query(query, (token_jti,))
            return True
        except Exception:
            return False

    @staticmethod
    async def revoke_all_user_tokens(user_id: int) -> int:
        query = "UPDATE refresh_tokens SET is_revoked = TRUE WHERE user_id = $1"
        try:
            await async_execute_query(query, (user_id,))
            return 1
        except Exception:
            return 0

    @staticmethod
    async def cleanup_expired_tokens() -> int:
        query = "DELETE FROM refresh_tokens WHERE expires_at < NOW()"
        try:
            await async_execute_query(query)
            return 1
        except Exception:
            return 0

    @staticmethod
    async def get_user_active_tokens(user_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM refresh_tokens WHERE user_id = $1 AND is_revoked = FALSE ORDER BY created_at DESC"
        return await async_execute_query_with_result(query, (user_id,))

    @staticmethod
    async def is_token_revoked(token_jti: str) -> bool:
        query = "SELECT is_revoked FROM refresh_tokens WHERE token_jti = $1"
        result = await async_execute_query_single_result(query, (token_jti,))
        return result is not None and result.get('is_revoked', True)