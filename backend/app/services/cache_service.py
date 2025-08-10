"""
Servicio de caché para mejorar el rendimiento de las consultas.
Implementa caché en memoria y Redis para reducir tiempos de respuesta.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Dict, List
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

# Caché en memoria para desarrollo local
_memory_cache: Dict[str, Dict[str, Any]] = {}

class CacheService:
    """Servicio de caché para mejorar el rendimiento."""
    
    def __init__(self, use_redis: bool = False):
        self.use_redis = use_redis
        self.redis_client = None
        
        if use_redis:
            try:
                import redis.asyncio as redis
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True
                )
                logger.info("Redis cache initialized")
            except ImportError:
                logger.warning("Redis not available, using memory cache")
                self.use_redis = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del caché."""
        try:
            if self.use_redis and self.redis_client:
                value = await self.redis_client.get(key)
                return json.loads(value) if value else None
            else:
                # Caché en memoria
                if key in _memory_cache:
                    cache_entry = _memory_cache[key]
                    if datetime.now(timezone.utc) < cache_entry['expires_at']:
                        return cache_entry['value']
                    else:
                        del _memory_cache[key]
                return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Establece un valor en el caché."""
        try:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            
            if self.use_redis and self.redis_client:
                await self.redis_client.setex(
                    key, 
                    ttl_seconds, 
                    json.dumps(value, default=str)
                )
            else:
                # Caché en memoria
                _memory_cache[key] = {
                    'value': value,
                    'expires_at': expires_at
                }
            
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Elimina un valor del caché."""
        try:
            if self.use_redis and self.redis_client:
                await self.redis_client.delete(key)
            else:
                _memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def clear(self, pattern: str = "*") -> bool:
        """Limpia el caché basado en un patrón."""
        try:
            if self.use_redis and self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
            else:
                # Para caché en memoria, limpiar todo
                _memory_cache.clear()
            return True
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return False
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera una clave única para el caché."""
        # Crear una representación string de los argumentos
        key_parts = [prefix]
        
        for arg in args:
            key_parts.append(str(arg))
        
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        key_string = "|".join(key_parts)
        
        # Crear hash para evitar claves muy largas
        return hashlib.md5(key_string.encode()).hexdigest()

# Instancia global del servicio de caché
cache_service = CacheService(use_redis=False)  # Por defecto usar caché en memoria

def cached(ttl_seconds: int = 300, key_prefix: str = "cache"):
    """Decorador para cachear funciones."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave única para la función y sus argumentos
            cache_key = cache_service.generate_key(
                f"{key_prefix}:{func.__name__}", 
                *args, 
                **kwargs
            )
            
            # Intentar obtener del caché
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Si no está en caché, ejecutar la función
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)
            
            # Guardar en caché
            await cache_service.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator

# Funciones de utilidad para caché específico
async def cache_news_data(news_data: List[Dict], ttl_seconds: int = 600):
    """Cachea datos de noticias."""
    await cache_service.set("news:latest", news_data, ttl_seconds)

async def get_cached_news_data() -> Optional[List[Dict]]:
    """Obtiene datos de noticias del caché."""
    return await cache_service.get("news:latest")

async def cache_projects_data(projects_data: List[Dict], ttl_seconds: int = 1800):
    """Cachea datos de proyectos."""
    await cache_service.set("projects:featured", projects_data, ttl_seconds)

async def get_cached_projects_data() -> Optional[List[Dict]]:
    """Obtiene datos de proyectos del caché."""
    return await cache_service.get("projects:featured")

async def invalidate_news_cache():
    """Invalida el caché de noticias."""
    await cache_service.delete("news:latest")

async def invalidate_projects_cache():
    """Invalida el caché de proyectos."""
    await cache_service.delete("projects:featured")
