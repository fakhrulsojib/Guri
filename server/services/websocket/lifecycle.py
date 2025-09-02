import structlog
from .manager import WebSocketManager

logger = structlog.get_logger()

async def initialize_websocket_manager(ws_manager: WebSocketManager):
    try:
        await ws_manager.connect_redis()
        await ws_manager.start_timeout_checker()
        logger.info("WebSocket manager initialized")
    except Exception as e:
        logger.error("Failed to initialize WebSocket manager", error=str(e))

async def cleanup_websocket_manager(ws_manager: WebSocketManager, active_connections: dict):
    try:
        await ws_manager.stop_timeout_checker()
        
        for connection_id in list(active_connections.keys()):
            await ws_manager.remove_connection(connection_id)
        
        await ws_manager.disconnect_redis()
        logger.info("WebSocket manager shutdown complete")
    except Exception as e:
        logger.error("Error during WebSocket manager shutdown", error=str(e)) 