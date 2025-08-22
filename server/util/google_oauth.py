import os
from typing import Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from fastapi import HTTPException, status
import httpx

class GoogleOAuthConfig:
    CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_TOKEN_INFO_URL: str = "https://oauth2.googleapis.com/tokeninfo"
    GOOGLE_USER_INFO_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"

class GoogleOAuthUtils:
    @staticmethod
    async def verify_google_token(id_token_str: str) -> Dict[str, Any]:
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                GoogleOAuthConfig.CLIENT_ID
            )
            
            if idinfo['aud'] != GoogleOAuthConfig.CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token audience"
                )
            
            if idinfo['exp'] < requests.Request().time:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return {
                "user_id": idinfo['sub'],
                "email": idinfo['email'],
                "email_verified": idinfo.get('email_verified', False),
                "name": idinfo.get('name', ''),
                "given_name": idinfo.get('given_name', ''),
                "family_name": idinfo.get('family_name', ''),
                "picture": idinfo.get('picture', ''),
                "locale": idinfo.get('locale', ''),
                "hd": idinfo.get('hd', '')
            }
            
        except GoogleAuthError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    
    @staticmethod
    async def verify_access_token(access_token: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                token_response = await client.get(
                    GoogleOAuthConfig.GOOGLE_TOKEN_INFO_URL,
                    params={"access_token": access_token}
                )
                
                if token_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid access token"
                    )
                
                token_info = token_response.json()
                
                if token_info.get('aud') != GoogleOAuthConfig.CLIENT_ID:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token audience"
                    )
                
                user_response = await client.get(
                    GoogleOAuthConfig.GOOGLE_USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if user_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to get user information"
                    )
                
                user_info = user_response.json()
                
                return {
                    "user_id": user_info['id'],
                    "email": user_info['email'],
                    "email_verified": user_info.get('verified_email', False),
                    "name": user_info.get('name', ''),
                    "given_name": user_info.get('given_name', ''),
                    "family_name": user_info.get('family_name', ''),
                    "picture": user_info.get('picture', ''),
                    "locale": user_info.get('locale', ''),
                    "hd": user_info.get('hd', '')
                }
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    
    @staticmethod
    async def exchange_code_for_tokens(authorization_code: str, redirect_uri: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": GoogleOAuthConfig.CLIENT_ID,
                        "client_secret": GoogleOAuthConfig.CLIENT_SECRET,
                        "code": authorization_code,
                        "grant_type": "authorization_code",
                        "redirect_uri": redirect_uri
                    }
                )
                
                if token_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to exchange code for tokens"
                    )
                
                token_data = token_response.json()
                
                user_info = await GoogleOAuthUtils.verify_access_token(token_data['access_token'])
                
                return {
                    "access_token": token_data['access_token'],
                    "refresh_token": token_data.get('refresh_token'),
                    "user_info": user_info
                }
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to exchange tokens: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token exchange failed: {str(e)}"
            ) 