import json
import uuid
import structlog
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect, status
import asyncio
import time
from datetime import datetime
from .manager import WebSocketManager
from .auth import authenticate_websocket, authorize_log_source_access

logger = structlog.get_logger()

async def handle_log_websocket_connection(
    websocket: WebSocket, 
    source_id: int, 
    ws_manager: WebSocketManager,
    active_connections: Dict,
    connection_metadata: Dict,
    connection_timeouts: Dict
):
    connection_id = str(uuid.uuid4())
    
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted", connection_id=connection_id, source_id=source_id)
        
        user = await authenticate_websocket(websocket)
        if not user:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Authentication failed"
            }))
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        if not await authorize_log_source_access(user, source_id):
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Access denied to this log source"
            }))
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        active_connections[connection_id] = websocket
        connection_metadata[connection_id] = {
            "user_id": user["id"],
            "source_id": source_id,
            "connected_at": str(uuid.uuid4())
        }
        
        connection_timeouts[connection_id] = datetime.utcnow()
        
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "connection_id": connection_id,
            "source_id": source_id,
            "message": "Connected to log stream"
        }))
        
        ws_manager.set_connection_storage(active_connections, connection_metadata, connection_timeouts)
        await ws_manager.subscribe_to_logs(source_id, connection_id)
        
        pubsub_task = asyncio.create_task(ws_manager.listen_to_logs(source_id, connection_id))
        
        try:
            TIMEOUT_THRESHOLD = 60
            while True:
                if connection_id in connection_timeouts:
                    last_ping = connection_timeouts[connection_id]
                    if (datetime.utcnow() - last_ping).total_seconds() > TIMEOUT_THRESHOLD:
                        logger.info(f"Connection timed out", connection_id=connection_id)
                        break
                
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=45.0)
                    message = json.loads(data)
                    
                    if message.get("type") == "ping":
                        await ws_manager.update_ping_time(connection_id)
                        
                        await websocket.send_text(json.dumps({
                            "type": "pong",
                            "timestamp": str(uuid.uuid4())
                        }))
                        
                except asyncio.TimeoutError:
                    pass
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected", connection_id=connection_id)
        except Exception as e:
            logger.error(f"Error handling WebSocket message", error=str(e), connection_id=connection_id)
        finally:
            pubsub_task.cancel()
            try:
                await pubsub_task
            except asyncio.CancelledError:
                pass
                
    except Exception as e:
        logger.error(f"WebSocket connection error", error=str(e), connection_id=connection_id)
    finally:
        await ws_manager.remove_connection(connection_id) 