import secrets
import time
from typing import Dict, Any, Optional
from fastapi import Request
import structlog

logger = structlog.get_logger()

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)

def validate_csrf_token(token: str, stored_data: Dict[str, Any]) -> bool:
    if not token or not stored_data:
        return False
        
    if token not in stored_data:
        return False
        
    token_info = stored_data[token]
    if time.time() - token_info["created_at"] > token_info.get("expiry", 3600):
        return False
        
    return True

def get_csrf_header_name() -> str:
    return "X-CSRF-Token"

def extract_csrf_token_from_request(request: Request) -> Optional[str]:
    return request.headers.get(get_csrf_header_name()) 