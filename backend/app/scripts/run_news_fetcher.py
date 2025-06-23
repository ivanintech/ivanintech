import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

# Añadir el directorio raíz del proyecto al path para que los imports funcionen
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings
from app.services.aggregated_news_service import fetch_and_store_news
from app.crud.crud_user import user as crud_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """
    Función principal para inicializar la sesión de BD y ejecutar el servicio de noticias.
    """
    logger.info("Iniciando el proceso de obtención de noticias...")

    # Forzar la carga de la URL de la base de datos desde las variables de entorno
    db_url = os.getenv("DATABASE_URL", settings.SQLALCHEMY_DATABASE_URI)
    if not db_url:
        logger.error("La variable de entorno DATABASE_URL no está configurada.")
        return

    # Usamos create_async_engine para la conexión asíncrona
    engine = create_async_engine(db_url, pool_pre_ping=True)
    AsyncSessionFactory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionFactory() as session:
        try:
            # Necesitamos un usuario para asociar las noticias (el superusuario)
            superuser = await crud_user.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
            if not superuser:
                logger.error(f"Superusuario '{settings.FIRST_SUPERUSER}' no encontrado. Abortando.")
                return

            logger.info("Superusuario encontrado. Iniciando la obtención y almacenamiento de noticias.")
            await fetch_and_store_news(db=session, user=superuser)
            logger.info("Proceso de obtención de noticias completado con éxito.")
        except Exception as e:
            logger.error(f"Ocurrió un error durante la ejecución del fetcher: {e}", exc_info=True)
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main()) 