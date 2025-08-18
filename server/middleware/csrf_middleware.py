import secrets
import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import structlog

logger = structlog.get_logger()

class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str, token_expiry: int = 3600):
        super().__init__(app)
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self._token_cache: Dict[str, Dict[str, Any]] = {}
        
    async def dispatch(self, request: Request, call_next):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            response = await call_next(request)
            if request.method == "GET":
                response.headers["X-CSRF-Token"] = self._generate_csrf_token(request)
            return response
            
        if not self._validate_csrf_token(request):
            logger.warning("CSRF validation failed", 
                         client_ip=request.client.host,
                         user_agent=request.headers.get("user-agent"),
                         path=request.url.path)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token validation failed"}
            )
            
        response = await call_next(request)
        return response
        
    def _generate_csrf_token(self, request: Request) -> str:
        token = secrets.token_urlsafe(32)
        client_id = self._get_client_identifier(request)
        
        self._token_cache[token] = {
            "client_id": client_id,
            "created_at": time.time(),
            "path": str(request.url.path)
        }
        
        self._cleanup_expired_tokens()
        return token
        
    def _validate_csrf_token(self, request: Request) -> bool:
        token = request.headers.get("X-CSRF-Token")
        if not token:
            return False
            
        if token not in self._token_cache:
            return False
            
        token_data = self._token_cache[token]
        client_id = self._get_client_identifier(request)
        
        if token_data["client_id"] != client_id:
            return False
            
        if time.time() - token_data["created_at"] > self.token_expiry:
            del self._token_cache[token]
            return False
            
        del self._token_cache[token]
        return True
        
    def _get_client_identifier(self, request: Request) -> str:
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        return f"{client_ip}:{user_agent}"
        
    def _cleanup_expired_tokens(self):
        current_time = time.time()
        expired_tokens = [
            token for token, data in self._token_cache.items()
            if current_time - data["created_at"] > self.token_expiry
        ]
        for token in expired_tokens:
            del self._token_cache[token] 