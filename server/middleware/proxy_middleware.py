from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class ProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.headers.get("x-forwarded-proto") == "https":
            request.scope["scheme"] = "https"
            request.scope["type"] = "http"
        
        response = await call_next(request)
        return response 