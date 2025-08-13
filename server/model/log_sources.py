from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class LogSourceType(str, Enum):
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    MICROSERVICE = "microservice"
    DATABASE = "database"
    INFRASTRUCTURE = "infrastructure"
    CUSTOM = "custom"

class LogSourceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    MAINTENANCE = "maintenance"

class LogSourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Log source name")
    description: Optional[str] = Field(None, max_length=500, description="Description of the log source")
    source_type: LogSourceType = Field(..., description="Type of log source")
    environment: str = Field(..., description="Environment (dev, staging, prod)")
    tags: List[str] = Field(default=[], description="Tags for categorization")

class LogSourceCreate(LogSourceBase):
    pass

class LogSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    source_type: Optional[LogSourceType] = None
    environment: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[LogSourceStatus] = None

class LogSourceInDB(LogSourceBase):
    id: int = Field(..., description="Internal log source ID")
    user_id: int = Field(..., description="Owner user ID")
    api_key: str = Field(..., description="Generated API key")
    status: LogSourceStatus = Field(default=LogSourceStatus.ACTIVE)
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_log_at: Optional[datetime] = Field(None, description="Last log received timestamp")
    log_count: int = Field(default=0, description="Total logs received")

class LogSourceResponse(LogSourceBase):
    id: int
    user_id: int
    status: LogSourceStatus
    created_at: datetime
    updated_at: datetime
    last_log_at: Optional[datetime]
    log_count: int
    # Note: api_key is intentionally excluded from responses for security

class LogSourceResponseWithKey(LogSourceBase):
    id: int
    user_id: int
    api_key: str = Field(..., description="Generated API key")
    status: LogSourceStatus
    created_at: datetime
    updated_at: datetime
    last_log_at: Optional[datetime]
    log_count: int 