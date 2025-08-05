import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
import secrets

from database.UserCrud import RefreshTokenCRUD

class JWTConfig:
    SECRET_KEY: str = os.getenv("JWT_SECRET", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    TOKEN_TYPE_ACCESS: str = "access"
    TOKEN_TYPE_REFRESH: str = "refresh"

class JWTUtils:
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": JWTConfig.TOKEN_TYPE_ACCESS,
            "iat": datetime.now(timezone.utc)
        })
        
        encoded_jwt = jwt.encode(to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        jti = secrets.token_urlsafe(32)
        
        to_encode.update({
            "exp": expire,
            "type": JWTConfig.TOKEN_TYPE_REFRESH,
            "iat": datetime.now(timezone.utc),
            "jti": jti
        })
        
        encoded_jwt = jwt.encode(to_encode, JWTConfig.SECRET_KEY, algorithm=JWTConfig.ALGORITHM)
        return encoded_jwt, jti, expire
    
    @staticmethod
    def verify_token(token: str, token_type: str = JWTConfig.TOKEN_TYPE_ACCESS) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, JWTConfig.SECRET_KEY, algorithms=[JWTConfig.ALGORITHM])
            
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
        
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def create_token_pair(user_id: str, email: str, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        base_data = {
            "sub": user_id,
            "email": email
        }
        
        if additional_data:
            base_data.update(additional_data)
        
        access_token = JWTUtils.create_access_token(base_data)
        refresh_token, jti, expires_at = JWTUtils.create_refresh_token(base_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "jti": jti,
            "expires_at": expires_at
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, str]:
        payload = JWTUtils.verify_token(refresh_token, JWTConfig.TOKEN_TYPE_REFRESH)
        jti = payload.get("jti")
        
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token format"
            )
        
        if RefreshTokenCRUD.is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )
        
        new_access_token = JWTUtils.create_access_token({
            "sub": user_id,
            "email": email
        })
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        } 