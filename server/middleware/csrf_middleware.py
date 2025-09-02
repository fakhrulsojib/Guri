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
        try:
            if request.url.path.startswith("/api/v1/logs"):
                return await call_next(request)
                
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                response = await call_next(request)
                if request.method == "GET":
                    try:
                        csrf_token = self._generate_csrf_token(request)
                        response.headers["X-CSRF-Token"] = csrf_token
                        logger.debug("CSRF token added to response", path=request.url.path)
                    except Exception as e:
                        logger.error("Failed to generate CSRF token", error=str(e), path=request.url.path)
                        return JSONResponse(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"detail": "CSRF token generation failed"}
                        )
                return response
                
            if not self._validate_csrf_token(request):
                logger.warning("CSRF validation failed", 
                             client_ip=request.client.host if request.client else "unknown",
                             user_agent=request.headers.get("user-agent"),
                             path=request.url.path)
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF token validation failed"}
                )
                
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error("CSRF middleware error", error=str(e), path=request.url.path)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "CSRF middleware error"}
            )
        
    def _generate_csrf_token(self, request: Request) -> str:
        try:
            token = secrets.token_urlsafe(32)
            client_id = self._get_client_identifier(request)
            
            self._token_cache[token] = {
                "client_id": client_id,
                "created_at": time.time(),
                "path": str(request.url.path)
            }
            
            self._cleanup_expired_tokens()
            return token
        except Exception as e:
            logger.error("Failed to generate CSRF token", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate CSRF token"
            )
        
    def _validate_csrf_token(self, request: Request) -> bool:
        try:
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
        except Exception as e:
            logger.error("CSRF validation error", error=str(e))
            return False
        
    def _get_client_identifier(self, request: Request) -> str:
        try:
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            return f"{client_ip}:{user_agent}"
        except Exception as e:
            logger.error("Failed to get client identifier", error=str(e))
            return "unknown:unknown"
        
    def _cleanup_expired_tokens(self):
        try:
            current_time = time.time()
            expired_tokens = [
                token for token, data in self._token_cache.items()
                if current_time - data["created_at"] > self.token_expiry
            ]
            for token in expired_tokens:
                del self._token_cache[token]
        except Exception as e:
            logger.error("Failed to cleanup expired tokens", error=str(e)) 