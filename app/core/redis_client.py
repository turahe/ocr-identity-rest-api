import redis.asyncio as redis
from typing import Optional, Any
from .config import get_redis_config


class RedisManager:
    """Redis connection manager"""
    
    def __init__(self):
        self.config = get_redis_config()
        self.client: Optional[redis.Redis] = None
    
    async def create_client(self) -> redis.Redis:
        """Create and return a Redis client"""
        if self.client is None:
            self.client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.db,
                decode_responses=self.config.decode_responses,
                max_connections=self.config.max_connections,
                retry_on_timeout=True,
                health_check_interval=30
            )
        return self.client
    
    async def get_client(self) -> redis.Redis:
        """Get the Redis client"""
        if self.client is None:
            await self.create_client()
        return self.client
    
    async def close_client(self):
        """Close the Redis client"""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None):
        """Set a key-value pair"""
        client = await self.get_client()
        return await client.set(key, value, ex=ex)
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key"""
        client = await self.get_client()
        return await client.get(key)
    
    async def delete(self, key: str) -> int:
        """Delete a key"""
        client = await self.get_client()
        return await client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        client = await self.get_client()
        return bool(await client.exists(key))
    
    async def expire(self, key: str, time: int) -> bool:
        """Set expiration time for a key"""
        client = await self.get_client()
        return await client.expire(key, time)
    
    async def ping(self) -> bool:
        """Ping Redis server"""
        try:
            client = await self.get_client()
            return await client.ping()
        except Exception:
            return False


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis() -> RedisManager:
    """Get the Redis manager instance"""
    return redis_manager


async def init_redis():
    """Initialize Redis client"""
    await redis_manager.create_client()


async def close_redis():
    """Close Redis client"""
    await redis_manager.close_client() 