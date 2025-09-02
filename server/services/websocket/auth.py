import structlog
from typing import Optional, Dict
from services.auth_service import get_current_user
from services.log_source_service import LogSourceService

logger = structlog.get_logger()

async def authenticate_websocket(websocket) -> Optional[Dict]:
    try:
        access_token = websocket.query_params.get("token")
        
        if not access_token:
            cookies = websocket.headers.get("cookie", "")
            for cookie in cookies.split(";"):
                if "access_token=" in cookie:
                    access_token = cookie.split("access_token=")[1].split(";")[0]
                    break
        
        if not access_token:
            return None
        
        class MockRequest:
            def __init__(self, token):
                self.cookies = {"access_token": token}
        
        mock_request = MockRequest(access_token)
        user = get_current_user(mock_request)
        return user
        
    except Exception as e:
        logger.error(f"WebSocket authentication failed", error=str(e))
        return None

async def authorize_log_source_access(user: Dict, source_id: int) -> bool:
    try:
        log_source = LogSourceService.get_log_source(source_id, user["id"])
        return log_source is not None
    except Exception as e:
        logger.error(f"Authorization check failed", error=str(e), user_id=user["id"], source_id=source_id)
        return False 