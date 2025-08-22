from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class LogSourceType(str, Enum):
    APPLICATION = "application"
    SYSTEM = "system"
    SECURITY = "security"
    AUDIT = "audit"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogSourceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class LogSourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Log source name")
    description: Optional[str] = Field(None, max_length=500, description="Description of the log source")
    source_type: LogSourceType = Field(..., description="Type of log source (application, system, security, audit, performance, custom)")
    environment: Environment = Field(..., description="Environment (development, staging, production, testing)")
    tags: List[str] = Field(default=[], max_items=10, description="Tags for categorization (max 10 tags)")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return []
        for tag in v:
            if len(tag) > 20:
                raise ValueError(f'Tag "{tag}" exceeds maximum length of 20 characters')
            if not tag.strip():
                raise ValueError('Tags cannot be empty or contain only whitespace')
        
        seen = set()
        unique_tags = []
        for tag in v:
            trimmed_tag = tag.strip()
            if trimmed_tag and trimmed_tag not in seen:
                seen.add(trimmed_tag)
                unique_tags.append(trimmed_tag)
        
        return unique_tags

class LogSourceCreate(LogSourceBase):
    pass

class LogSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    source_type: Optional[LogSourceType] = None
    environment: Optional[Environment] = None
    tags: Optional[List[str]] = None
    status: Optional[LogSourceStatus] = None

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        for tag in v:
            if len(tag) > 20:
                raise ValueError(f'Tag "{tag}" exceeds maximum length of 20 characters')
            if not tag.strip():
                raise ValueError('Tags cannot be empty or contain only whitespace')
        
        seen = set()
        unique_tags = []
        for tag in v:
            trimmed_tag = tag.strip()
            if trimmed_tag and trimmed_tag not in seen:
                seen.add(trimmed_tag)
                unique_tags.append(trimmed_tag)
        
        return unique_tags

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

class LogSourceResponseWithKey(LogSourceBase):
    id: int
    user_id: int
    api_key: str = Field(..., description="Generated API key")
    status: LogSourceStatus
    created_at: datetime
    updated_at: datetime
    last_log_at: Optional[datetime]
    log_count: int 