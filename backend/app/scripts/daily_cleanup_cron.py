#!/usr/bin/env python3
"""
Script para el cron job diario de limpieza de noticias antiguas.
Este script está diseñado para ser ejecutado por Render como un cron job.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/daily_cleanup_cron.log')  # Log file para debugging
    ]
)
logger = logging.getLogger(__name__)

async def cleanup_old_news(days_to_keep: int = 30):
    """
    Limpia noticias más antiguas que el número de días especificado.
    """
    start_time = datetime.now(timezone.utc)
    logger.info(f"🧹 Iniciando limpieza de noticias antiguas (más de {days_to_keep} días): {start_time}")
    
    # Verificar variables de entorno críticas
    if not os.getenv("DATABASE_URL"):
        logger.error("❌ DATABASE_URL no está configurada")
        return {"error": "DATABASE_URL not configured", "deleted_count": 0}
    
    try:
        # Configurar conexión a la base de datos
        engine = create_async_engine(
            os.getenv("DATABASE_URL"),
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
                # Contar noticias antes de la limpieza
                count_before = await session.execute(text("SELECT COUNT(*) FROM news"))
                count_before = count_before.scalar()
                
                # Eliminar noticias antiguas
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
                
                # Eliminar noticias más antiguas que el cutoff_date
                result = await session.execute(
                    text("DELETE FROM news WHERE \"publishedAt\" < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                
                deleted_count = result.rowcount
                await session.commit()
                
                # Contar noticias después de la limpieza
                count_after = await session.execute(text("SELECT COUNT(*) FROM news"))
                count_after = count_after.scalar()
                
                end_time = datetime.now(timezone.utc)
                duration = (end_time - start_time).total_seconds()
                
                logger.info(f"✅ Limpieza completada exitosamente en {duration:.2f} segundos")
                logger.info(f"   Noticias eliminadas: {deleted_count}")
                logger.info(f"   Noticias antes: {count_before}")
                logger.info(f"   Noticias después: {count_after}")
                logger.info(f"   Fecha de corte: {cutoff_date}")
                
                return {
                    "deleted_count": deleted_count,
                    "count_before": count_before,
                    "count_after": count_after,
                    "cutoff_date": cutoff_date.isoformat(),
                    "duration_seconds": duration
                }
                
            except Exception as e:
                logger.error(f"❌ Error durante la limpieza: {e}", exc_info=True)
                await session.rollback()
                return {"error": str(e), "deleted_count": 0}
            finally:
                await session.close()
                
    except Exception as e:
        logger.error(f"❌ Error configurando la base de datos: {e}", exc_info=True)
        return {"error": str(e), "deleted_count": 0}
    finally:
        await engine.dispose()

async def main():
    """
    Función principal para el cron job de limpieza.
    """
    try:
        result = await cleanup_old_news(days_to_keep=30)
        
        if "error" in result:
            logger.error(f"❌ Error en la limpieza: {result['error']}")
            sys.exit(1)
        else:
            logger.info(f"✅ Limpieza exitosa: {result['deleted_count']} noticias eliminadas")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Error fatal en el cron job de limpieza: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Cron job de limpieza interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error fatal en el cron job de limpieza: {e}", exc_info=True)
        sys.exit(1)
