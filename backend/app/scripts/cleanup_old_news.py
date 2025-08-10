#!/usr/bin/env python3
"""
Script para limpiar noticias antiguas de la base de datos.
Mantiene solo las noticias de los últimos 30 días para optimizar el rendimiento.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.db.models.news_item import NewsItem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def cleanup_old_news(days_to_keep: int = 30):
    """
    Elimina noticias más antiguas que el número de días especificado.
    
    Args:
        days_to_keep: Número de días de noticias a mantener (default: 30)
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
    
    async with async_session_maker() as db:
        try:
            # Contar noticias antes de la limpieza
            count_before = await db.scalar(
                text("SELECT COUNT(*) FROM news_items")
            )
            
            # Eliminar noticias antiguas
            delete_stmt = delete(NewsItem).where(
                NewsItem.publishedAt < cutoff_date
            )
            
            result = await db.execute(delete_stmt)
            deleted_count = result.rowcount
            
            await db.commit()
            
            # Contar noticias después de la limpieza
            count_after = await db.scalar(
                text("SELECT COUNT(*) FROM news_items")
            )
            
            logger.info(f"Cleanup completed:")
            logger.info(f"  - Noticias antes: {count_before}")
            logger.info(f"  - Noticias eliminadas: {deleted_count}")
            logger.info(f"  - Noticias después: {count_after}")
            logger.info(f"  - Fecha de corte: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return {
                "deleted_count": deleted_count,
                "remaining_count": count_after,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error durante la limpieza: {e}", exc_info=True)
            raise


async def get_news_statistics():
    """
    Obtiene estadísticas de las noticias en la base de datos.
    """
    async with async_session_maker() as db:
        try:
            # Total de noticias
            total = await db.scalar(text("SELECT COUNT(*) FROM news_items"))
            
            # Noticias de hoy
            today = datetime.now(timezone.utc).date()
            today_count = await db.scalar(
                text("SELECT COUNT(*) FROM news_items WHERE DATE(\"publishedAt\") = :today"),
                {"today": today}
            )
            
            # Noticias de esta semana
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            week_count = await db.scalar(
                text("SELECT COUNT(*) FROM news_items WHERE \"publishedAt\" >= :week_ago"),
                {"week_ago": week_ago}
            )
            
            # Noticia más antigua
            oldest = await db.scalar(
                text("SELECT MIN(\"publishedAt\") FROM news_items")
            )
            
            # Noticia más reciente
            newest = await db.scalar(
                text("SELECT MAX(\"publishedAt\") FROM news_items")
            )
            
            return {
                "total_news": total,
                "today_count": today_count,
                "week_count": week_count,
                "oldest_news": oldest.isoformat() if oldest else None,
                "newest_news": newest.isoformat() if newest else None
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
            raise


async def main():
    """
    Función principal del script.
    """
    logger.info("=== Script de Limpieza de Noticias ===")
    
    try:
        # Mostrar estadísticas antes de la limpieza
        logger.info("Estadísticas actuales:")
        stats = await get_news_statistics()
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        # Ejecutar limpieza
        logger.info("\nEjecutando limpieza...")
        result = await cleanup_old_news(days_to_keep=30)
        
        # Mostrar estadísticas después de la limpieza
        logger.info("\nEstadísticas después de la limpieza:")
        stats_after = await get_news_statistics()
        for key, value in stats_after.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("=== Limpieza completada exitosamente ===")
        
    except Exception as e:
        logger.error(f"Error en el script: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 