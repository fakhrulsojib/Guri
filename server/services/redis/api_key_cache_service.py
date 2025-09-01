from typing import Optional, Dict, Any
import structlog
from .base_redis_service import BaseRedisService

logger = structlog.get_logger()

class ApiKeyCacheService(BaseRedisService):
    def get_api_key_cache(self, api_key: str) -> Optional[Dict[str, Any]]:
        try:
            cache_key = f"api_key:{api_key}"
            cached_data = self.client.hgetall(cache_key)
            
            if not cached_data:
                return None
            
            return {
                "source_id": int(cached_data.get("source_id")),
                "active": cached_data.get("active") == "true"
            }
        except Exception as e:
            logger.error("Redis get error", error=str(e))
            return None
    
    def set_api_key_cache(self, api_key: str, source_id: int, active: bool, ttl: int = 300) -> bool:
        try:
            cache_key = f"api_key:{api_key}"
            cache_data = {
                "source_id": str(source_id),
                "active": str(active).lower()
            }
            
            self.client.hset(cache_key, mapping=cache_data)
            self.client.expire(cache_key, ttl)
            
            return True
        except Exception as e:
            logger.error("Redis set error", error=str(e))
            return False
    
    def invalidate_api_key_cache(self, api_key: str) -> bool:
        try:
            cache_key = f"api_key:{api_key}"
            self.client.delete(cache_key)
            return True
        except Exception as e:
            logger.error("Redis delete error", error=str(e))
            return False

api_key_cache_service = ApiKeyCacheService() 