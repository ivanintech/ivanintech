# backend/app/scripts/fetch_news.py
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker
from app.services.aggregated_news_service import fetch_and_store_news
from app.crud.crud_user import user as crud_user

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """
    Función principal para ejecutar el proceso de obtención de noticias.
    """
    logger.info("Iniciando el script para obtener y almacenar noticias...")
    
    db: AsyncSession = async_session_maker()
    
    try:
        # Para que el servicio funcione, necesita un usuario al que asociar las noticias.
        # Por defecto, usaremos el primer superusuario que encontremos.
        # En un sistema más complejo, esto podría gestionarse de otra forma.
        first_superuser = await crud_user.get_first_superuser(db)
        
        if not first_superuser:
            logger.error("No se ha encontrado un superusuario en la base de datos.")
            logger.error("Por favor, cree un superusuario antes de ejecutar este script.")
            return

        logger.info(f"Ejecutando el servicio de noticias como usuario: {first_superuser.email}")
        
        # Llamamos a la función principal del servicio de noticias
        await fetch_and_store_news(user=first_superuser)
        
    except Exception as e:
        logger.error(f"Ha ocurrido un error durante la ejecución del script: {e}", exc_info=True)
    finally:
        await db.close()
        logger.info("Script de obtención de noticias finalizado.")

if __name__ == "__main__":
    asyncio.run(main()) 