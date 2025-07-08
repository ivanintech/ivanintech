from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
import asyncio
import sys
import os

# Agregar el directorio backend al path si no está
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/simple/", response_model=List[Dict[str, Any]])
async def get_simple_projects() -> List[Dict[str, Any]]:
    """
    Endpoint simple que obtiene proyectos directamente desde Supabase
    Sin dependencias de base de datos local
    """
    logger.info("[API Simple] Obteniendo proyectos desde Supabase")
    
    try:
        projects = await supabase_service.get_projects()
        logger.info(f"[API Simple] Obtenidos {len(projects)} proyectos")
        return projects
    except Exception as e:
        logger.error(f"[API Simple] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo proyectos: {str(e)}")

@router.get("/simple/featured/", response_model=List[Dict[str, Any]])
async def get_simple_featured_projects() -> List[Dict[str, Any]]:
    """
    Endpoint simple que obtiene solo proyectos destacados desde Supabase
    """
    logger.info("[API Simple] Obteniendo proyectos destacados desde Supabase")
    
    try:
        projects = await supabase_service.get_featured_projects()
        logger.info(f"[API Simple] Obtenidos {len(projects)} proyectos destacados")
        return projects
    except Exception as e:
        logger.error(f"[API Simple] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo proyectos destacados: {str(e)}")

@router.get("/simple/test/")
async def simple_test():
    """
    Endpoint de prueba simple
    """
    return {"message": "Simple endpoint working!", "status": "ok"} 