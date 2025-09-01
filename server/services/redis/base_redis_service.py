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
        
        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            password=self.redis_password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    def health_check(self) -> bool:
        try:
            return self.client.ping()
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False 