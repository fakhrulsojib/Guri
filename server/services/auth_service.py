from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from util.jwt_utils import JWTUtils, JWTConfig
from util.google_oauth import GoogleOAuthUtils
from database.UserCrud import UserCRUD, RefreshTokenCRUD
from model.user import UserCreate, UserUpdate, TokenResponse, RefreshTokenResponse

security = HTTPBearer()

class AuthService:
    @staticmethod
    def _create_or_update_user(google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        user = UserCRUD.get_user_by_google_id(google_user_info["user_id"])
        
        if not user:
            user_data = UserCreate(
                google_id=google_user_info["user_id"],
                email=google_user_info["email"],
                email_verified=google_user_info["email_verified"],
                name=google_user_info["name"],
                given_name=google_user_info["given_name"],
                family_name=google_user_info["family_name"],
                picture=google_user_info["picture"],
                locale=google_user_info["locale"],
                hd=google_user_info["hd"]
            )
            user = UserCRUD.create_user(user_data)
        else:
            user_update = UserUpdate(
                name=google_user_info["name"],
                given_name=google_user_info["given_name"],
                family_name=google_user_info["family_name"],
                picture=google_user_info["picture"],
                locale=google_user_info["locale"],
                hd=google_user_info["hd"],
                last_login=datetime.now(timezone.utc)
            )
            UserCRUD.update_user(user["id"], user_update)
        
        return user

    @staticmethod
    def _validate_user_active(user: Dict[str, Any]) -> None:
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

    @staticmethod
    def _create_token_response(user: Dict[str, Any]) -> TokenResponse:
        token_data = JWTUtils.create_token_pair(
            user_id=str(user["id"]),
            email=user["email"],
            additional_data={
                "google_id": user["google_id"],
                "name": user["name"]
            }
        )
        
        RefreshTokenCRUD.store_refresh_token(
            token_data["jti"],
            user["id"],
            token_data["refresh_token"],
            token_data["expires_at"]
        )
        
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_in=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    @staticmethod
    async def authenticate_with_google_id_token(id_token: str) -> TokenResponse:
        google_user_info = await GoogleOAuthUtils.verify_google_token(id_token)
        user = AuthService._create_or_update_user(google_user_info)
        AuthService._validate_user_active(user)

        return AuthService._create_token_response(user)

    @staticmethod
    async def authenticate_with_google_access_token(access_token: str) -> TokenResponse:
        google_user_info = await GoogleOAuthUtils.verify_access_token(access_token)
        user = AuthService._create_or_update_user(google_user_info)
        AuthService._validate_user_active(user)

        return AuthService._create_token_response(user)

    @staticmethod
    async def authenticate_with_authorization_code(authorization_code: str, redirect_uri: str) -> TokenResponse:
        token_data = await GoogleOAuthUtils.exchange_code_for_tokens(
            authorization_code=authorization_code,
            redirect_uri=redirect_uri
        )
        
        google_user_info = token_data["user_info"]
        user = AuthService._create_or_update_user(google_user_info)
        AuthService._validate_user_active(user)

        return AuthService._create_token_response(user)

    @staticmethod
    def refresh_access_token(refresh_token: str) -> RefreshTokenResponse:
        return JWTUtils.refresh_access_token(refresh_token)

    @staticmethod
    def logout(refresh_token: str) -> Dict[str, str]:
        try:
            payload = JWTUtils.verify_token(refresh_token, JWTConfig.TOKEN_TYPE_REFRESH)
            jti = payload.get("jti")
            
            if jti:
                RefreshTokenCRUD.revoke_refresh_token(jti)
            
            return {"message": "Successfully logged out"}
        
        except Exception:
            return {"message": "Successfully logged out"}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = JWTUtils.verify_token(credentials.credentials, JWTConfig.TOKEN_TYPE_ACCESS)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = UserCRUD.get_user_by_id(int(user_id))
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user 