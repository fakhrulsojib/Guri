import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse

from services.auth_service import AuthService, get_current_active_user

GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

from model.user import (
    GoogleAuthRequest, 
    TokenResponse, 
    RefreshTokenRequest, 
    RefreshTokenResponse,
    LogoutRequest,
    UserResponse
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/google/login", response_model=TokenResponse)
async def google_login(auth_request: GoogleAuthRequest):
    try:
        if auth_request.id_token:
            return await AuthService.authenticate_with_google_id_token(
                auth_request.id_token
            )
        
        elif auth_request.access_token:
            return await AuthService.authenticate_with_google_access_token(
                auth_request.access_token
            )
        
        elif auth_request.authorization_code and auth_request.redirect_uri:
            return await AuthService.authenticate_with_authorization_code(
                auth_request.authorization_code,
                auth_request.redirect_uri
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either id_token, access_token, or authorization_code with redirect_uri"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@auth_router.get("/google/callback")
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
        
        redirect_uri = str(request.url).split('?')[0] if request else GOOGLE_REDIRECT_URI
        
        auth_response = await AuthService.authenticate_with_authorization_code(
            authorization_code=code,
            redirect_uri=redirect_uri
        )
        
        frontend_redirect = state if state else FRONTEND_URL
        
        if auth_response and auth_response.access_token:
            return RedirectResponse(url=f"{frontend_redirect}?auth=success&access_token={auth_response.access_token}&refresh_token={auth_response.refresh_token}")
        else:
            return RedirectResponse(url=f"{frontend_redirect}?error=auth_failed")
        
    except Exception as e:
        frontend_redirect = state if state else FRONTEND_URL
        return RedirectResponse(url=f"{frontend_redirect}?error=auth_failed")

@auth_router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(refresh_request: RefreshTokenRequest):
    try:
        return AuthService.refresh_access_token(refresh_request.refresh_token)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@auth_router.post("/logout")
async def logout(logout_request: LogoutRequest):
    try:
        return AuthService.logout(logout_request.refresh_token)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        email_verified=current_user["email_verified"],
        name=current_user["name"],
        given_name=current_user["given_name"],
        family_name=current_user["family_name"],
        picture=current_user["picture"],
        locale=current_user["locale"],
        hd=current_user["hd"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        last_login=current_user["last_login"]
    ) 