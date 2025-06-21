from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Aumentar el timeout para SQLite para mitigar errores de "database is locked"
connect_args = {}
if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
    connect_args["timeout"] = 15

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# --- CREACIÓN DE LA SESIÓN SÍNCRONA ---
SYNC_DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI).replace("sqlite+aiosqlite", "sqlite")
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
# --- FIN DE LA SESIÓN SÍNCRONA ---

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        yield session 