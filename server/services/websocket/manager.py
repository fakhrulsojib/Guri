import json
import uuid
import structlog
from typing import Dict
import redis.asyncio as redis
import os
import asyncio
from datetime import datetime, timedelta

logger = structlog.get_logger()

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

PING_TIMEOUT_SECONDS = 45 

class WebSocketManager:
    def __init__(self):
        self.redis_client = None
        self.connection_pubsubs = {}
        self.timeout_checker_task = None
        self._redis_connection_pool = None
    
    async def connect_redis(self):
        try:
            if self.redis_client and await self._test_connection():
                return
                
            redis_kwargs = {
                'host': REDIS_HOST,
                'port': REDIS_PORT,
                'db': REDIS_DB,
                'decode_responses': True,
                'socket_connect_timeout': 10,
                'socket_timeout': 10,
                'retry_on_timeout': True,
                'socket_keepalive': True,
                'socket_keepalive_options': {},
                'health_check_interval': 30,
                'max_connections': 20
            }
            
            if REDIS_PASSWORD:
                redis_kwargs['password'] = REDIS_PASSWORD
                
            self._redis_connection_pool = redis.ConnectionPool(**redis_kwargs)
            self.redis_client = redis.Redis(connection_pool=self._redis_connection_pool)
            await self.redis_client.ping()
            logger.info("Redis connection established for WebSocket manager")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise
    
    async def _test_connection(self):
        try:
            await self.redis_client.ping()
            return True
        except:
            return False
    
    async def disconnect_redis(self):
        for connection_id, pubsub in self.connection_pubsubs.items():
            try:
                await pubsub.close()
            except:
                pass
        self.connection_pubsubs.clear()
            
        if self.redis_client:
            try:
                await self.redis_client.close()
            except:
                pass
            self.redis_client = None
            
        if self._redis_connection_pool:
            try:
                await self._redis_connection_pool.disconnect()
            except:
                pass
            self._redis_connection_pool = None
            
        logger.info("Redis connection closed for WebSocket manager")
    
    async def start_timeout_checker(self):
        async def check_timeouts():
            while True:
                try:
                    current_time = datetime.utcnow()
                    timed_out_connections = []
                    
                    if hasattr(self, 'connection_timeouts'):
                        for connection_id, last_ping in self.connection_timeouts.items():
                            if current_time - last_ping > timedelta(seconds=PING_TIMEOUT_SECONDS):
                                timed_out_connections.append(connection_id)
                        
                        for connection_id in timed_out_connections:
                            logger.info(f"Connection timed out due to no ping", connection_id=connection_id)
                            await self.remove_connection(connection_id)
                    
                    if hasattr(self, 'timeout_checker_counter'):
                        self.timeout_checker_counter += 1
                    else:
                        self.timeout_checker_counter = 0
                    
                    if self.timeout_checker_counter >= 30 and hasattr(self, 'connection_metadata') and self.redis_client:
                        await self._refresh_all_subscription_ttls()
                        self.timeout_checker_counter = 0
                    
                    await asyncio.sleep(10)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in timeout checker", error=str(e))
                    await asyncio.sleep(10)
        
        self.timeout_checker_task = asyncio.create_task(check_timeouts())
    
    async def stop_timeout_checker(self):
        if self.timeout_checker_task:
            self.timeout_checker_task.cancel()
            try:
                await self.timeout_checker_task
            except asyncio.CancelledError:
                pass
    
    async def update_ping_time(self, connection_id: str):
        if hasattr(self, 'connection_timeouts'):
            self.connection_timeouts[connection_id] = datetime.utcnow()
    
    async def subscribe_to_logs(self, source_id: int, connection_id: str):
        try:
            if not self.redis_client or not await self._test_connection():
                await self.connect_redis()
            
            channel_name = f"logs:source:{source_id}"
            
            pubsub = self.redis_client.pubsub()
            self.connection_pubsubs[connection_id] = pubsub
            
            await pubsub.subscribe(channel_name)
            
            subscription_key = f"subs:source:{source_id}"
            await self.redis_client.sadd(subscription_key, connection_id)
            await self.redis_client.expire(subscription_key, 600)
            
            logger.info(f"Subscribed to logs channel", source_id=source_id, connection_id=connection_id)
                    
        except Exception as e:
            logger.error(f"Error in subscribe_to_logs", error=str(e), source_id=source_id, connection_id=connection_id)
            raise
    
    async def listen_to_logs(self, source_id: int, connection_id: str):
        try:
            if connection_id not in self.connection_pubsubs:
                logger.warning("PubSub not available for listening", connection_id=connection_id)
                return
            
            pubsub = self.connection_pubsubs[connection_id]
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    log_data = json.loads(message["data"])
                    ws_message = {
                        "type": "log",
                        **log_data
                    }
                    await self.broadcast_to_connection(connection_id, json.dumps(ws_message))
                elif message["type"] == "subscribe":
                    logger.info(f"Successfully subscribed to channel", channel=message["channel"])
                    
        except asyncio.CancelledError:
            logger.info(f"Redis listening cancelled", source_id=source_id, connection_id=connection_id)
        except Exception as e:
            logger.error(f"Error in listen_to_logs", error=str(e), source_id=source_id, connection_id=connection_id)
    
    async def broadcast_to_connection(self, connection_id: str, message: str):
        if hasattr(self, 'active_connections') and connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to connection", connection_id=connection_id, error=str(e))
                await self.remove_connection(connection_id)
    
    async def remove_connection(self, connection_id: str):
        if connection_id in self.connection_pubsubs:
            try:
                await self.connection_pubsubs[connection_id].close()
            except:
                pass
            del self.connection_pubsubs[connection_id]
        
        if hasattr(self, 'active_connections') and connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            del self.active_connections[connection_id]
            
            if hasattr(self, 'connection_metadata') and connection_id in self.connection_metadata:
                metadata = self.connection_metadata[connection_id]
                source_id = metadata.get("source_id")
                if source_id:
                    try:
                        if self.redis_client:
                            await self.redis_client.srem(f"subs:source:{source_id}", connection_id)
                    except Exception as e:
                        logger.error(f"Failed to remove from Redis subscription", error=str(e))
                
                del self.connection_metadata[connection_id]
            
            if hasattr(self, 'connection_timeouts') and connection_id in self.connection_timeouts:
                del self.connection_timeouts[connection_id]
            
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection", error=str(e))
            
            logger.info(f"WebSocket connection removed", connection_id=connection_id)
    
    async def _refresh_all_subscription_ttls(self):
        try:
            if not self.redis_client:
                return
             
            source_ids = set()
            for metadata in self.connection_metadata.values():
                source_id = metadata.get("source_id")
                if source_id:
                    source_ids.add(source_id)

            for source_id in source_ids:
                subscription_key = f"subs:source:{source_id}"
                subscriber_count = await self.redis_client.scard(subscription_key)
                if subscriber_count > 0:
                    await self.redis_client.expire(subscription_key, 600)
                    logger.debug(f"Refreshed TTL for subscription", source_id=source_id, subscriber_count=subscriber_count)
                    
        except Exception as e:
            logger.error(f"Failed to refresh subscription TTLs", error=str(e))

    def set_connection_storage(self, active_connections: Dict, connection_metadata: Dict, connection_timeouts: Dict):
        self.active_connections = active_connections
        self.connection_metadata = connection_metadata
        self.connection_timeouts = connection_timeouts 