from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any
import logging
import re
import uuid

from app.api import deps
from app.schemas.project import ProjectRead, ProjectCreate, ProjectUpdate, PaginatedProjects
from app.services import github_service
from app.services.supabase_service import supabase_service
from app.db.models.user import User
from app import crud
from app.db import models

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/",
    response_model=PaginatedProjects,
    summary="Get a paginated list of projects with optional filters",
)
async def read_projects(
    db: deps.SessionDep,
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    per_page: int = Query(
        10, ge=1, le=100, description="Number of projects per page"
    ),
    is_featured: bool = Query(None, description="Filter by featured projects"),
):
    """
    Retrieve a paginated list of projects.
    """
    total, projects = await crud.project.get_multi_paginated(
        db,
        skip=(page - 1) * per_page,
        limit=per_page,
        is_featured=is_featured,
    )
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": projects,
    }

@router.post(
    "/sync-github/",
    response_model=List[ProjectRead],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def sync_github_projects(db: deps.SessionDep, current_user: deps.CurrentUser) -> Any:
    """
    Manually trigger a sync of projects from GitHub and return the updated list.
    """
    logger.info(
        f"[API Projects] User {current_user.email} is triggering GitHub project sync."
    )

    github_username = "ivanintech"  # Or from config
    github_repos = await github_service.get_user_repositories(github_username)

    if not github_repos:
        logger.info(f"No repositories found on GitHub for user {github_username}.")
        return await crud.project.get_multi(db=db)

    newly_added_count = 0
    already_exists_count = 0

    for repo in github_repos:
        existing_project = await crud.project.get_by_title(
            db=db, title=repo.name
        ) or await crud.project.get_by_github_url(db=db, github_url=str(repo.html_url))

        if existing_project:
            already_exists_count += 1
            continue

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
                    gif_urls = re.findall(
                        r"\!\[.*?\]\((.*?\.gif(?:\?raw=true)?)\)",
                        readme_content,
                        re.IGNORECASE,
                    )
                    if gif_urls:
                        videoUrl = github_service.construct_full_gif_url(
                            gif_urls[0], owner, repo_name, repo.default_branch
                        )

        project_in = ProjectCreate(
            title=repo.name,
            description=repo.description or "N/A",
            githubUrl=str(repo.html_url),
            technologies=repo.topics
            + ([repo.language] if repo.language and repo.language not in repo.topics else []),
            videoUrl=videoUrl,
            is_featured=False,
        )

        await crud.project.create(db=db, obj_in=project_in)
        newly_added_count += 1

    logger.info(
        f"GitHub project sync completed. Added: {newly_added_count}, Skipped existing: {already_exists_count}"
    )

    total, projects = await crud.project.get_multi_paginated(db=db, limit=100)
    return projects

@router.put(
    "/{project_id}/toggle-featured/",
    response_model=ProjectRead,
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def toggle_project_featured(project_id: str, db: deps.SessionDep, current_user: deps.CurrentUser) -> Any:
    """
    Toggles the is_featured status of a project.
    """
    logger.info(
        f"[API Projects] User {current_user.email} is toggling 'is_featured' for project ID: {project_id}"
    )

    updated_project = await crud.project.toggle_featured(db=db, project_id=project_id)

    if not updated_project:
        logger.warning(
            f"[API Projects] Project with ID {project_id} not found to toggle 'is_featured'."
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    logger.info(
        f"[API Projects] Successfully toggled 'is_featured' for project ID {project_id} to {updated_project.is_featured}"
    )
    return updated_project

@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def create_project(
    *,
    db: deps.SessionDep,
    project_in: ProjectCreate,
    current_user: deps.CurrentUser,
) -> Any:
    """
    Create a new project.
    """
    logger.info(
        f"[API Projects] User {current_user.email} is creating a new project: {project_in.title}"
    )
    project = await crud.project.create(db=db, obj_in=project_in)
    return project

@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Update a project",
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
):
    """
    Update an existing project.
    """
    logger.info(
        f"[API Projects] User {current_user.email} is updating project ID: {project_id}"
    )

    project = await crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    updated_project = await crud.project.update(db=db, db_obj=project, obj_in=project_in)
    logger.info(f"[API Projects] Successfully updated project ID: {project_id}")
    return updated_project

@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def delete_project(
    project_id: str,
    db: deps.SessionDep,
    current_user: deps.CurrentUser,
):
    """
    Delete a project.
    """
    logger.info(
        f"[API Projects] User {current_user.email} is deleting project ID: {project_id}"
    )

    project = await crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    await crud.project.remove(db=db, id=project_id)
    logger.info(f"[API Projects] Successfully deleted project ID: {project_id}")

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str,
    db: deps.SessionDep,
) -> Any:
    """
    Get a specific project by ID.
    """
    project = await crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project

@router.put(
    "/{project_id}/toggle-visibility",
    response_model=ProjectRead,
    summary="Toggle the visibility of a project",
    dependencies=[Depends(deps.get_current_active_superuser)],
)
async def toggle_project_visibility(
    project_id: str,
    db: deps.SessionDep,
):
    """
    Toggle the visibility of a project
    """
    # Implementation of toggle_project_visibility function
    pass

@router.get("/{project_id}", response_model=ProjectRead)
async def read_project(
    project_id: str,
    db: deps.SessionDep
):
    """
    Get a specific project by its ID
    """
    project = await crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project 