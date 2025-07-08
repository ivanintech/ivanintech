#!/usr/bin/env python3
"""
Script para probar el sistema de fetching de noticias manualmente
"""
import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.aggregated_news_service import fetch_and_store_news
from app import crud

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Función principal para probar el fetching de noticias"""
    logger.info("=== INICIANDO PRUEBA DE FETCHING DE NOTICIAS ===")
    
    try:
        # Crear sesión de base de datos
        async with AsyncSessionLocal() as session:
            # Obtener el superusuario
            superuser = await crud.user.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
            if not superuser:
                logger.error("No se encontró el superusuario. Asegúrate de que esté configurado.")
                return
            
            logger.info(f"Superusuario encontrado: {superuser.email}")
            
            # Ejecutar el fetching de noticias
            logger.info("Iniciando fetching de noticias...")
            await fetch_and_store_news(db=session, user=superuser)
            
            logger.info("=== PRUEBA COMPLETADA ===")
            
    except Exception as e:
        logger.error(f"Error durante la prueba: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 