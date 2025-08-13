from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class RawLog(BaseModel):
    api_key: str = Field(..., min_length=1, description="Log source API key for authentication")
    level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    message: str = Field(..., description="Log message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Structured log data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Log timestamp")
    trace_id: Optional[str] = Field(None, description="Trace ID for request tracking")
    span_id: Optional[str] = Field(None, description="Span ID for distributed tracing")

    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v or not v.strip():
            raise ValueError('API key cannot be empty or whitespace only')
        return v.strip()
