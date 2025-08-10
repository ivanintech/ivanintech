#!/usr/bin/env python3
"""
Script para diagnosticar y optimizar el rendimiento de la aplicación.
Analiza problemas de rendimiento y propone soluciones.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any

from app.db.session import async_session_maker
from app.db.models.news_item import NewsItem
from app.db.models.project import Project
from app.db.models.blog_post import BlogPost
from app.db.models.resource_link import ResourceLink
from app.crud.crud_news import news
from app.crud.crud_project import project
from app.crud.crud_resource_link import resource_link

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def diagnose_performance():
    """Diagnostica el rendimiento actual de la aplicación."""
    logger.info("🔍 DIAGNÓSTICO DE RENDIMIENTO")
    logger.info("=" * 60)
    
    async with async_session_maker() as db:
        # 1. Análisis de la base de datos
        logger.info("1. 📊 ANÁLISIS DE LA BASE DE DATOS:")
        
        # Contar registros por tabla
        tables = [
            ("NewsItem", NewsItem),
            ("Project", Project), 
            ("BlogPost", BlogPost),
            ("ResourceLink", ResourceLink)
        ]
        
        for table_name, model in tables:
            start_time = time.time()
            result = await db.execute(select(func.count(model.id)))
            count = result.scalar()
            query_time = (time.time() - start_time) * 1000
            logger.info(f"   {table_name}: {count} registros ({query_time:.2f}ms)")
        
        # 2. Análisis de consultas lentas
        logger.info("\n2. ⏱️  ANÁLISIS DE CONSULTAS LENTAS:")
        
        # Test de consulta de noticias
        start_time = time.time()
        news_items = await news.get_multi(db, skip=0, limit=20)
        news_query_time = (time.time() - start_time) * 1000
        logger.info(f"   Consulta de noticias (20 items): {news_query_time:.2f}ms")
        
        # Test de consulta de proyectos
        start_time = time.time()
        projects = await project.get_multi(db, skip=0, limit=10)
        projects_query_time = (time.time() - start_time) * 1000
        logger.info(f"   Consulta de proyectos (10 items): {projects_query_time:.2f}ms")
        
        # Test de consulta de blog posts (comentado por ahora)
        # start_time = time.time()
        # blog_posts = await blog.get_multi(db, skip=0, limit=10)
        # blog_query_time = (time.time() - start_time) * 1000
        # logger.info(f"   Consulta de blog posts (10 items): {blog_query_time:.2f}ms")
        blog_query_time = 0  # Placeholder
        
        # 3. Análisis de índices
        logger.info("\n3. 📈 ANÁLISIS DE ÍNDICES:")
        
        # Verificar índices existentes
        try:
            result = await db.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
            """))
            indexes = result.fetchall()
            
            if indexes:
                logger.info(f"   Índices encontrados: {len(indexes)}")
                for idx in indexes[:5]:  # Mostrar solo los primeros 5
                    logger.info(f"   - {idx[1]}.{idx[2]}")
            else:
                logger.warning("   No se encontraron índices")
                
        except Exception as e:
            logger.error(f"   Error al verificar índices: {e}")
        
        # 4. Análisis de conexiones
        logger.info("\n4. 🔗 ANÁLISIS DE CONEXIONES:")
        
        try:
            result = await db.execute(text("""
                SELECT 
                    count(*) as active_connections,
                    count(*) FILTER (WHERE state = 'active') as active_queries
                FROM pg_stat_activity 
                WHERE datname = current_database();
            """))
            conn_stats = result.fetchone()
            logger.info(f"   Conexiones activas: {conn_stats[0]}")
            logger.info(f"   Consultas activas: {conn_stats[1]}")
        except Exception as e:
            logger.error(f"   Error al verificar conexiones: {e}")
        
        # 5. Recomendaciones
        logger.info("\n5. 💡 RECOMENDACIONES DE OPTIMIZACIÓN:")
        
        # Evaluar tiempos de consulta
        slow_queries = []
        if news_query_time > 100:
            slow_queries.append("Noticias")
        if projects_query_time > 100:
            slow_queries.append("Proyectos")
        if blog_query_time > 100:
            slow_queries.append("Blog posts")
        
        if slow_queries:
            logger.warning(f"   ⚠️  Consultas lentas detectadas: {', '.join(slow_queries)}")
            logger.info("   💡 Soluciones:")
            logger.info("      - Implementar caché Redis")
            logger.info("      - Optimizar consultas con índices")
            logger.info("      - Implementar paginación eficiente")
            logger.info("      - Usar consultas selectivas")
        else:
            logger.info("   ✅ Todas las consultas están en rangos aceptables")
        
        # 6. Optimizaciones específicas
        logger.info("\n6. 🚀 OPTIMIZACIONES ESPECÍFICAS:")
        
        # Verificar si hay muchas noticias sin valoración
        result = await db.execute(
            select(func.count(NewsItem.id)).where(NewsItem.relevance_rating.is_(None))
        )
        unrated_news = result.scalar()
        
        if unrated_news > 50:
            logger.warning(f"   ⚠️  {unrated_news} noticias sin valoración")
            logger.info("   💡 Ejecutar: python app/scripts/populate_missing_ratings.py")
        
        # Verificar noticias antiguas
        result = await db.execute(
            select(func.count(NewsItem.id)).where(
                NewsItem.publishedAt < datetime.now(timezone.utc).replace(day=1)
            )
        )
        old_news = result.scalar()
        
        if old_news > 100:
            logger.warning(f"   ⚠️  {old_news} noticias antiguas")
            logger.info("   💡 Ejecutar: python app/scripts/cleanup_old_news.py")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ DIAGNÓSTICO COMPLETADO")

async def optimize_database():
    """Aplica optimizaciones a la base de datos."""
    logger.info("🔧 APLICANDO OPTIMIZACIONES")
    logger.info("=" * 60)
    
    async with async_session_maker() as db:
        try:
            # 1. Crear índices para mejorar el rendimiento
            logger.info("1. 📈 Creando índices de rendimiento...")
            
            indexes_to_create = [
                "CREATE INDEX IF NOT EXISTS idx_news_published_at ON news_item(published_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_news_relevance_rating ON news_item(relevance_rating DESC)",
                "CREATE INDEX IF NOT EXISTS idx_news_promotion_level ON news_item(promotion_level DESC)",
                "CREATE INDEX IF NOT EXISTS idx_project_is_featured ON project(is_featured DESC)",
                "CREATE INDEX IF NOT EXISTS idx_project_created_at ON project(created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_blog_published_date ON blog_post(published_date DESC)",
                "CREATE INDEX IF NOT EXISTS idx_blog_status ON blog_post(status)",
                "CREATE INDEX IF NOT EXISTS idx_resource_created_at ON resource_link(created_at DESC)",
                "CREATE INDEX IF NOT EXISTS idx_resource_likes ON resource_link(likes DESC)"
            ]
            
            for index_sql in indexes_to_create:
                try:
                    await db.execute(text(index_sql))
                    logger.info(f"   ✅ Índice creado: {index_sql.split('ON')[1].strip()}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Error creando índice: {e}")
            
            await db.commit()
            
            # 2. Analizar tablas para optimizar el planificador
            logger.info("\n2. 📊 Analizando tablas...")
            
            tables_to_analyze = ["news_item", "project", "blog_post", "resource_link"]
            for table in tables_to_analyze:
                try:
                    await db.execute(text(f"ANALYZE {table}"))
                    logger.info(f"   ✅ Tabla analizada: {table}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Error analizando {table}: {e}")
            
            await db.commit()
            
            logger.info("\n✅ OPTIMIZACIONES APLICADAS")
            
        except Exception as e:
            logger.error(f"❌ Error durante la optimización: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(diagnose_performance())
    print("\n" + "=" * 60)
    print("¿Quieres aplicar optimizaciones? (s/n): ", end="")
    response = input().lower().strip()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        asyncio.run(optimize_database())
    else:
        print("Optimizaciones omitidas.")
