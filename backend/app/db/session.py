from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator # Importar AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__) # Configurar logger

# Añadir log para depuración
print(f"[session.py] Intentando conectar a: {settings.SQLALCHEMY_DATABASE_URI}")

# Crear engine ASÍNCRONO
# connect_args no aplica directamente a aiosqlite de la misma forma, 
# aiosqlite está diseñado para asyncio y no tiene el problema de check_same_thread.
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI, # Usar la URL async directamente desde settings
    pool_pre_ping=True, 
    # echo=True # Descomentar para ver SQL generado (útil para debug)
)

# Crear async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False # Configuración común para FastAPI
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get an asynchronous database session."""
    logger.info("--- [get_db] Intentando obtener sesión DB --- ") # LOG AÑADIDO
    async with AsyncSessionLocal() as session:
        logger.info("--- [get_db] Sesión DB obtenida --- ") # LOG AÑADIDO
        try:
            # Log antes de entregar la sesión
            print(f"[get_db] Sesión creada ({type(session)}), bind: {session.bind}") 
            yield session
            logger.debug("--- [get_db] Sesión DB yielded --- ") # LOG AÑADIDO (DEBUG)
        except Exception as e:
            logger.error(f"--- [get_db] Error durante yield de sesión: {e} ---", exc_info=True) # LOG AÑADIDO
            await session.rollback() # Hacer rollback en caso de error durante el yield
            raise # Relanzar para que FastAPI lo maneje
        finally:
            logger.debug("--- [get_db] Cerrando sesión DB --- ") # LOG AÑADIDO (DEBUG)
            # No es necesario cerrar explícitamente con el context manager `async with`
            # await session.close() <-- Esto es redundante y puede causar errores
            pass 