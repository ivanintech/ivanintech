# app/api/routes/portfolio.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import logging # Importar logging

from app.schemas.project import ProjectRead
# from app.db_mock import projects_db # Ya no se usa
from app import crud # Importar módulo crud
from app.db.session import get_db # Importar dependencia de sesión

# Configurar logger para esta ruta
logger = logging.getLogger(__name__)

router = APIRouter()

# Convertir la ruta a async
@router.get("/projects", response_model=List[ProjectRead])
async def read_projects(db: AsyncSession = Depends(get_db)):
    """Retrieve projects from the database asynchronously via CRUD layer."""
    logger.info("***** [API /projects] Endpoint alcanzado *****") # Log simple
    try:
        projects = await crud.portfolio.get_projects(db=db)
        logger.info(f"***** [API /projects] CRUD devolvió: {projects} *****") # Log con datos
        return projects
    except Exception as e:
        logger.error(f"***** [API /projects] Error al obtener proyectos: {e} *****", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al obtener proyectos")

# Ejemplo de endpoint para un solo proyecto (síncrono)
# @router.get("/projects/{project_id}", response_model=ProjectRead)
# def read_project(project_id: str, db: Session = Depends(get_db)):
#     db_project = crud.portfolio.get_project(db=db, project_id=project_id)
#     if db_project is None:
#         raise HTTPException(status_code=404, detail="Project not found")
#     return db_project

# Podríamos añadir endpoints para obtener un proyecto por ID, crear, etc. 
# async def read_project(id: str, db: AsyncSession = Depends(get_db)) -> ProjectRead:
#     db_project = await crud.get_project(db=db, id=id)
#     if not db_project:
#         raise HTTPException(status_code=404, detail="Project not found")
#     return db_project 