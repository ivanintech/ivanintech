from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
import logging
import re

from app.api import deps
from app.schemas.project import ProjectRead, ProjectCreate
from app.services import github_service
from app.db.models.user import User
from app import crud

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[ProjectRead])
async def read_projects(
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Recupera todos los proyectos.
    """
    logger.info("[API Projects] Leyendo todos los proyectos de la BBDD.")
    
    current_projects = await crud.project.get_multi(db=db)
    logger.info(f"[API Projects] Devolviendo {len(current_projects)} proyectos desde la BBDD.")
    
    return current_projects

@router.post("/sync-github/", response_model=List[ProjectRead])
async def sync_github_projects(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Activa manualmente una sincronización de proyectos desde GitHub y devuelve la lista actualizada.
    """
    logger.info(f"[API Projects] User {current_user.email} is triggering GitHub project sync.")
    
    github_username = "ivanintech"
    github_repos = await github_service.get_user_repositories(github_username)
    
    if not github_repos:
        logger.info(f"No repositories found on GitHub for user {github_username}.")
        return await crud.project.get_multi(db=db)

    newly_added_count = 0
    already_exists_count = 0

    for repo in github_repos:
        existing_project = await crud.project.get_by_title(db=db, title=repo.name) or \
                           await crud.project.get_by_github_url(db=db, github_url=str(repo.html_url))
        
        if existing_project:
            already_exists_count += 1
            continue

        # Logic to find GIF URL, moved from service
        videoUrl = None
        owner_repo_tuple = github_service.extract_owner_repo_from_url(str(repo.html_url))
        if owner_repo_tuple:
            owner, repo_name = owner_repo_tuple
            root_contents = await github_service.get_repo_root_contents(owner, repo_name)
            for item in root_contents:
                if item.type == "file" and item.name.lower().endswith(".gif") and item.download_url:
                    videoUrl = str(item.download_url)
                    break
            if not videoUrl:
                readme_content = await github_service.get_readme_content(owner, repo_name)
                if readme_content:
                    gif_urls = re.findall(r"\!\[.*?\]\((.*?\.gif(?:\?raw=true)?)\)", readme_content, re.IGNORECASE)
                    if gif_urls:
                        videoUrl = github_service.construct_full_gif_url(gif_urls[0], owner, repo_name, repo.default_branch)

        project_in = ProjectCreate(
            title=repo.name,
            description=repo.description or "N/A",
            githubUrl=str(repo.html_url),
            technologies=repo.topics + ([repo.language] if repo.language and repo.language not in repo.topics else []),
            videoUrl=videoUrl,
            is_featured=False
        )
        
        await crud.project.create(db=db, obj_in=project_in)
        newly_added_count += 1
            
    logger.info(f"GitHub project sync completed. Added: {newly_added_count}, Skipped existing: {already_exists_count}")
    
    return await crud.project.get_multi(db=db)

@router.put("/{project_id}/toggle-featured/", response_model=ProjectRead)
async def toggle_project_featured(
    project_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Alterna el estado is_featured de un proyecto.
    """
    logger.info(f"[API Projects] User {current_user.email} is toggling 'is_featured' for project ID: {project_id}")
    
    updated_project = await crud.project.toggle_featured(db=db, project_id=project_id)
    
    if not updated_project:
        logger.warning(f"[API Projects] Project with ID {project_id} not found to toggle 'is_featured'.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    logger.info(f"[API Projects] Successfully toggled 'is_featured' for project ID {project_id} to {updated_project.is_featured}")
    return updated_project 