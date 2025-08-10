from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator
import logging
import asyncio
from typing import AsyncGenerator

from app.core.config import settings

logger = logging.getLogger(__name__)

if settings.SQLALCHEMY_DATABASE_URI:
    # Asynchronous engine: Optimized for performance
    async_connect_args = {
        "statement_cache_size": 0,  # PgBouncer compatibility
        "server_settings": {
            "jit": "off",  # Disable JIT for better performance on small queries
            "random_page_cost": "1.1",  # Optimize for SSD
            "effective_cache_size": "256MB",  # Optimize for Render's memory
        }
    }
    async_engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        pool_size=10,  # Increase pool size for better concurrency
        max_overflow=20,  # Allow more connections when needed
        pool_recycle=3600,  # Recycle connections every hour
        pool_timeout=30,  # Timeout for getting connection from pool
        connect_args=async_connect_args,
        echo=False,  # Disable SQL logging in production
    )
    async_session_maker = async_sessionmaker(
        autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
    )

    # Synchronous engine
    sync_db_uri = settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", "")
    
    # Also disable statement cache for the sync engine for consistency,
    # though it's mainly an asyncpg issue.
    sync_connect_args = {"statement_cache_size": 0}
    if sync_db_uri.startswith("sqlite"):
        sync_connect_args["check_same_thread"] = False

    sync_engine = create_engine(
        sync_db_uri,
        pool_pre_ping=True,
        connect_args=sync_connect_args,
    )
    SyncSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=sync_engine
    )

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get an asynchronous database session."""
    async with async_session_maker() as session:
        yield session 

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close() 