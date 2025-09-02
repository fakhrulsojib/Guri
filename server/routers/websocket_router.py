from fastapi import APIRouter, WebSocket
from services.websocket import (
    WebSocketManager,
    handle_log_websocket_connection
)
from services.websocket.state import (
    active_connections,
    connection_metadata,
    connection_timeouts
)

websocket_router = APIRouter(
    prefix="/api/v1",
    tags=["WebSocket"]
)

ws_manager = WebSocketManager()

@websocket_router.websocket("/follow/{source_id}")
async def websocket_endpoint(websocket: WebSocket, source_id: int):
    await handle_log_websocket_connection(
        websocket, 
        source_id, 
        ws_manager,
        active_connections,
        connection_metadata,
        connection_timeouts
    ) 