"""
Scripts de utilidades para el backend de IvanInTech.

ADVERTENCIA: Estos scripts están diseñados para desarrollo y tareas manuales.
NO deben ser ejecutados en producción o como parte del flujo principal de Docker.
"""

import functools
import logging
import os
from typing import Callable, Any

logger = logging.getLogger(__name__)

def development_only(func: Callable) -> Callable:
    """
    Decorador que previene la ejecución accidental en producción.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        environment = os.getenv("ENVIRONMENT", "local")
        
        if environment == "production":
            raise RuntimeError(
                f"⚠️  SCRIPT BLOQUEADO: '{func.__name__}' no debe ejecutarse en producción. "
                f"Este script es solo para desarrollo/testing."
            )
        
        if environment in ["staging", "production"]:
            logger.warning(
                f"🚨 CUIDADO: Ejecutando script de desarrollo '{func.__name__}' "
                f"en entorno '{environment}'. Procede solo si sabes lo que haces."
            )
        
        return func(*args, **kwargs)
    
    return wrapper 