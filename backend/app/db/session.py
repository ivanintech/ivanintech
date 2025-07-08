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
    # Asynchronous engine: Explicitly disable statement cache for asyncpg
    async_connect_args = {"statement_cache_size": 0}
    async_engine = create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        connect_args=async_connect_args,
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