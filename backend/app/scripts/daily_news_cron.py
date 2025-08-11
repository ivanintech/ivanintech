#!/usr/bin/env python3
"""
Script para el cron job diario de obtención de noticias.
Este script está diseñado para ser ejecutado por Render como un cron job.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.aggregated_news_service import fetch_and_store_news
from app.crud.crud_user import user as crud_user

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/daily_news_cron.log')  # Log file para debugging
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """
    Función principal para el cron job diario de noticias.
    """
    start_time = datetime.now(timezone.utc)
    logger.info(f"🚀 Iniciando cron job diario de noticias: {start_time}")
    
    # Verificar variables de entorno críticas
    required_env_vars = ["DATABASE_URL", "GEMINI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {missing_vars}")
        sys.exit(1)
    
    # Configurar conexión a la base de datos
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("❌ DATABASE_URL no está configurada")
        sys.exit(1)
    
    try:
        # Crear engine con configuración robusta
        engine = create_async_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_timeout=30,
            connect_args={
                "statement_cache_size": 0,
                "jit": "off",
                "random_page_cost": "1.1",
                "effective_cache_size": "256MB"
            }
        )
        
        AsyncSessionFactory = sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        async with AsyncSessionFactory() as session:
            try:
                # Buscar superusuario
                superuser = await crud_user.get_by_email(
                    db=session, 
                    email=settings.FIRST_SUPERUSER
                )
                
                if not superuser:
                    logger.error(f"❌ Superusuario '{settings.FIRST_SUPERUSER}' no encontrado")
                    sys.exit(1)
                
                logger.info(f"✅ Superusuario encontrado: {superuser.email}")
                
                # Ejecutar obtención de noticias
                logger.info("📰 Iniciando obtención y almacenamiento de noticias...")
                await fetch_and_store_news(user=superuser)
                
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                logger.info(f"✅ Cron job completado exitosamente en {duration:.2f} segundos")
                logger.info(f"   Inicio: {start_time}")
                logger.info(f"   Fin: {end_time}")
                
            except Exception as e:
                logger.error(f"❌ Error durante la ejecución del cron job: {e}", exc_info=True)
                sys.exit(1)
            finally:
                await session.close()
                
    except Exception as e:
        logger.error(f"❌ Error configurando la base de datos: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Cron job interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error fatal en el cron job: {e}", exc_info=True)
        sys.exit(1)
