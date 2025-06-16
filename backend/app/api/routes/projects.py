from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
import logging

from app.db.session import get_db
from app.schemas.project import ProjectRead
from app.services import project_service
from app.api import deps # For authentication, if needed for protected routes
from app.db.models.user import User # Corrected path for User model
from app.crud import crud_project # Added import for crud_project

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[ProjectRead])
async def read_projects(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Recupera todos los proyectos y activa una sincronización en segundo plano.
    """
    logger.info("[API Projects] Leyendo todos los proyectos de la BBDD.")
    
    current_projects = await crud_project.get_projects(db=db)
    validated_projects = [ProjectRead.model_validate(p) for p in current_projects]
    logger.info(f"[API Projects] Devolviendo {len(validated_projects)} proyectos desde la BBDD.")

    # Programar la sincronización de GitHub como una tarea en segundo plano
    # La función de servicio ahora maneja su propia sesión de BBDD
    logger.info("[API Projects] Programando sincronización de proyectos de GitHub en segundo plano.")
    background_tasks.add_task(project_service.sync_projects_from_github, "ivanintech")
    
    return validated_projects

@router.post("/sync-github/", response_model=List[ProjectRead])
async def sync_github_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Activa manualmente una sincronización de proyectos desde GitHub y devuelve la lista actualizada.
    """
    logger.info(f"[API Projects] El usuario {current_user.email} está activando la sincronización de proyectos de GitHub.")
    
    # Ejecutar la sincronización y esperar a que termine
    await project_service.sync_projects_from_github(github_username="ivanintech")
    
    # Después de la sincronización, obtener y devolver la lista actualizada de todos los proyectos
    logger.info("[API Projects] Sincronización completada. Obteniendo la lista de proyectos actualizada.")
    all_projects = await crud_project.get_projects(db=db)
    
    return [ProjectRead.model_validate(p) for p in all_projects]

@router.put("/{project_id}/toggle-featured/", response_model=ProjectRead)
async def toggle_project_featured(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Alterna el estado is_featured de un proyecto.
    """
    logger.info(f"[API Projects] El usuario {current_user.email} intenta alternar 'is_featured' para el proyecto ID: {project_id}")
    updated_project = await project_service.toggle_project_featured_status(db=db, project_id=project_id)
    if not updated_project:
        logger.warning(f"[API Projects] Proyecto con ID {project_id} no encontrado para alternar 'is_featured'.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    logger.info(f"[API Projects] Se ha alternado correctamente 'is_featured' para el proyecto ID {project_id} a {updated_project.is_featured}")
    return updated_project 