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
    """Retrieve all projects. Returns current DB state and triggers a background sync."""
    logger.info("[API Projects] Reading all projects from DB initially.")
    
    # 1. Fetch current projects from the database immediately
    # Assuming crud_project.get_projects(db) fetches all projects
    # You might need to adjust if crud_project is not directly available or named differently
    # For now, let's assume you have a way to get projects, e.g., via project_service
    # or directly via crud_project if it's structured for that.
    
    # Let's use crud_project.get_projects directly if it exists and is appropriate.
    # Need to ensure crud_project is imported if used here.
    # from app.crud import crud_project # Make sure this import is present or adjust path
    
    current_projects = await crud_project.get_projects(db=db) # Direct call to CRUD
    validated_projects = [ProjectRead.model_validate(p) for p in current_projects]
    logger.info(f"[API Projects] Returning {len(validated_projects)} projects from DB.")

    # 2. Schedule the GitHub sync as a background task
    logger.info("[API Projects] Scheduling GitHub project sync in background.")
    background_tasks.add_task(project_service.sync_projects_from_github, db, "ivancastroprojects")
    
    return validated_projects

@router.post("/sync-github/", response_model=List[ProjectRead])
async def sync_github_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser) # Protect this endpoint
) -> Any:
    """Manually trigger a sync of projects from GitHub for the configured user."""
    logger.info(f"[API Projects] User {current_user.email} triggering GitHub projects sync for 'ivancastroprojects'")
    projects = await project_service.sync_projects_from_github(db=db, github_username="ivancastroprojects")
    logger.info(f"[API Projects] GitHub sync completed. Returning {len(projects)} projects.")
    return projects

@router.put("/{project_id}/toggle-featured/", response_model=ProjectRead)
async def toggle_project_featured(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser) # Protect this endpoint
) -> Any:
    """Toggle the is_featured status of a project."""
    logger.info(f"[API Projects] User {current_user.email} attempting to toggle 'is_featured' for project ID: {project_id}")
    updated_project = await project_service.toggle_project_featured_status(db=db, project_id=project_id)
    if not updated_project:
        logger.warning(f"[API Projects] Project with ID {project_id} not found for toggling 'is_featured'.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    logger.info(f"[API Projects] Successfully toggled 'is_featured' for project ID {project_id} to {updated_project.is_featured}")
    return updated_project 