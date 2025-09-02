import redis
import os
import structlog

logger = structlog.get_logger()

class BaseRedisService:
    def __init__(self):
        self.redis_host = os.environ.get("REDIS_HOST", "redis")
        self.redis_port = int(os.environ.get("REDIS_PORT", 6379))
        self.redis_db = int(os.environ.get("REDIS_DB", 0))
        self.redis_password = os.environ.get("REDIS_PASSWORD")
        
        redis_kwargs = {
            'host': self.redis_host,
            'port': self.redis_port,
            'db': self.redis_db,
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True
        }
        
        if self.redis_password:
            redis_kwargs['password'] = self.redis_password
        
        self.client = redis.Redis(**redis_kwargs)
    
    def health_check(self) -> bool:
        try:
            return self.client.ping()
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False 