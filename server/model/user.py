from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    name: Optional[str] = Field(None, description="User's full name")
    given_name: Optional[str] = Field(None, description="User's given name")
    family_name: Optional[str] = Field(None, description="User's family name")
    picture: Optional[str] = Field(None, description="User's profile picture URL")
    locale: Optional[str] = Field(None, description="User's locale")
    hd: Optional[str] = Field(None, description="Hosted domain")

class UserCreate(UserBase):
    google_id: str = Field(..., description="Google user ID")
    email_verified: bool = Field(False, description="Whether email is verified")

class UserUpdate(BaseModel):
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
    hd: Optional[str] = None
    last_login: Optional[datetime] = None

class UserInDB(UserBase):
    id: int = Field(..., description="Internal user ID")
    google_id: str = Field(..., description="Google user ID")
    email_verified: bool = Field(..., description="Whether email is verified")
    is_active: bool = Field(True, description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

class UserResponse(UserBase):
    id: int = Field(..., description="Internal user ID")
    email_verified: bool = Field(..., description="Whether email is verified")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

class RefreshToken(BaseModel):
    token_jti: str = Field(..., description="JWT ID from refresh token")
    user_id: int = Field(..., description="User ID")
    refresh_token: str = Field(..., description="Encrypted refresh token")
    expires_at: datetime = Field(..., description="Token expiration time")
    created_at: datetime = Field(..., description="Token creation time")
    is_revoked: bool = Field(False, description="Whether token is revoked")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")

class GoogleAuthRequest(BaseModel):
    id_token: Optional[str] = Field(None, description="Google ID token")
    access_token: Optional[str] = Field(None, description="Google access token")
    authorization_code: Optional[str] = Field(None, description="Authorization code from Google OAuth")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI used in OAuth flow") 