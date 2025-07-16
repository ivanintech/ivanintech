import asyncio
import os
import sys
import logging

# --- Adjust path to allow app imports ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import MetaData
from sqlalchemy import text

from app.core.config import settings
from app.db.base import Base  # Asegura que se cargan los modelos

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def drop_all_tables():
    """Se conecta a la base de datos y borra todas las tablas conocidas."""
    
    db_url = settings.SQLALCHEMY_DATABASE_URI
    if not db_url or "sqlite" in db_url:
        logger.error("Error: El script está configurado para una base de datos local SQLite. No se ejecutará.")
        logger.error("Asegúrate de que DATABASE_URL en config.py apunta a tu base de datos PostgreSQL remota.")
        return

    logger.warning(f"--- ATENCIÓN: A punto de borrar TODAS las tablas de la base de datos: ...{str(db_url)[-20:]}")
    logger.warning("--- Tienes 5 segundos para cancelar (Ctrl+C)...")
    await asyncio.sleep(5)
    logger.info("--- Procediendo con el borrado de tablas...")

    # Usamos el motor asíncrono que ya está configurado
    engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={"statement_cache_size": 0},
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        # Usamos `reflect` para obtener el estado actual, pero para un borrado total
        # es más seguro iterar sobre nuestros modelos conocidos.
        # El borrado se hace en orden inverso de creación de metadatos.
        for table in reversed(Base.metadata.sorted_tables):
            try:
                logger.info(f"Borrando tabla: {table.name}...")
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table.name}" CASCADE'))
                logger.info(f"Tabla {table.name} borrada.")
            except Exception as e:
                logger.error(f"No se pudo borrar la tabla {table.name}. Puede que no existiera. Error: {e}")
        
        # También borramos la tabla de historial de Alembic
        try:
            logger.info("Borrando tabla de versiones de Alembic (alembic_version)...")
            await conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
            logger.info("Tabla alembic_version borrada.")
        except Exception as e:
            logger.error(f"No se pudo borrar la tabla alembic_version. Error: {e}")

        # También borramos los tipos ENUM personalizados
        try:
            logger.info("Borrando tipos ENUM personalizados (votetype)...")
            await conn.execute(text('DROP TYPE IF EXISTS votetype'))
            logger.info("Tipo votetype borrado.")
        except Exception as e:
            logger.error(f"No se pudo borrar el tipo votetype. Error: {e}")


    await engine.dispose()
    logger.info("--- ¡Toda la base de datos ha sido borrada con éxito!")


if __name__ == "__main__":
    asyncio.run(drop_all_tables()) 