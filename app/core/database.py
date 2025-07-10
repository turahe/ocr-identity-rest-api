import asyncpg
from typing import Optional
from .config import get_database_config


class DatabaseManager:
    """Database connection manager for PostgreSQL"""
    
    def __init__(self):
        self.config = get_database_config()
        self.pool: Optional[asyncpg.Pool] = None
    
    async def create_pool(self) -> asyncpg.Pool:
        """Create and return a connection pool"""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                min_size=5,
                max_size=self.config.pool_size,
                command_timeout=60,
                server_settings={
                    'application_name': 'ocr_identity_api'
                }
            )
        return self.pool
    
    async def get_connection(self) -> asyncpg.Connection:
        """Get a connection from the pool"""
        if self.pool is None:
            await self.create_pool()
        if self.pool is None:
            raise RuntimeError("Failed to create database pool")
        return await self.pool.acquire()
    
    async def close_pool(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def execute(self, query: str, *args, **kwargs):
        """Execute a query"""
        if self.pool is None:
            await self.create_pool()
        if self.pool is None:
            raise RuntimeError("Failed to create database pool")
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args, **kwargs)
    
    async def fetch(self, query: str, *args, **kwargs):
        """Fetch rows from a query"""
        if self.pool is None:
            await self.create_pool()
        if self.pool is None:
            raise RuntimeError("Failed to create database pool")
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args, **kwargs)
    
    async def fetchrow(self, query: str, *args, **kwargs):
        """Fetch a single row from a query"""
        if self.pool is None:
            await self.create_pool()
        if self.pool is None:
            raise RuntimeError("Failed to create database pool")
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args, **kwargs)
    
    async def fetchval(self, query: str, *args, **kwargs):
        """Fetch a single value from a query"""
        if self.pool is None:
            await self.create_pool()
        if self.pool is None:
            raise RuntimeError("Failed to create database pool")
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args, **kwargs)


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> DatabaseManager:
    """Get the database manager instance"""
    return db_manager


async def init_database():
    """Initialize database connection pool"""
    await db_manager.create_pool()


async def close_database():
    """Close database connection pool"""
    await db_manager.close_pool() 