import os
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
import structlog

from services.auth_service import AuthService
from util.jwt_utils import JWTConfig

GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "localhost")

from model.user import (
    TokenResponse, 
    UserResponse
)

logger = structlog.get_logger()

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/google/callback", include_in_schema=False)
async def google_oauth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    request: Request = None
):
    try:
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth error: {error}"
            )
        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code is required"
            )
        
        auth_response = await AuthService.authenticate_with_authorization_code(
            authorization_code=code,
            redirect_uri=f"{request.base_url}auth/google/callback"
        )
        
        response = RedirectResponse(url=f"{FRONTEND_URL}?auth=success")
        
        response.set_cookie(
            key="access_token",
            value=auth_response.access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
            domain=COOKIE_DOMAIN
        )
        response.set_cookie(
            key="refresh_token",
            value=auth_response.refresh_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=JWTConfig.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/auth/refresh",
            domain=COOKIE_DOMAIN
        )
        
        logger.info("OAuth callback successful, cookies set, redirecting to frontend")
        return response
            
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        frontend_redirect = state if state else FRONTEND_URL
        return RedirectResponse(url=f"{frontend_redirect}?error=auth_failed")



@auth_router.post("/refresh")
async def refresh_token(request: Request):
    """Refresh access token using refresh token from cookies"""
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No refresh token found in cookies"
            )
        
        new_tokens = AuthService.refresh_access_token(refresh_token)
        
        response_obj = Response(
            content='{"message": "Token refreshed successfully"}', 
            media_type="application/json"
        )
        
        response_obj.set_cookie(
            key="access_token",
            value=new_tokens["access_token"],
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
            domain=COOKIE_DOMAIN
        )
        
        return response_obj
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@auth_router.post("/logout")
async def logout(request: Request):
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token found in cookies"
            )
        
        result = AuthService.logout(refresh_token)
        
        response_obj = Response(content='{"message": "Successfully logged out"}', media_type="application/json")
        
        response_obj.delete_cookie("access_token", path="/", domain=COOKIE_DOMAIN)
        response_obj.delete_cookie("refresh_token", path="/auth/refresh", domain=COOKIE_DOMAIN)
        
        return response_obj
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed: {str(e)}"
        )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token found in cookies"
        )
    
    try:
        from util.jwt_utils import JWTUtils
        payload = JWTUtils.verify_token(access_token, "access")
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        from database.UserCrud import UserCRUD
        user = UserCRUD.get_user_by_id(int(user_id))
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            email_verified=user["email_verified"],
            name=user["name"],
            given_name=user["given_name"],
            family_name=user["family_name"],
            picture=user["picture"],
            locale=user["locale"],
            hd=user["hd"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            last_login=user["last_login"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        ) 