from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import logging

from app.db.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)

async def get_projects(db: AsyncSession) -> List[Project]:
    """Retrieve all projects from the database."""
    logger.debug("[CRUD Project] Fetching all projects")
    result = await db.execute(select(Project).order_by(Project.is_featured.desc(), Project.title))
    projects = result.scalars().all()
    logger.debug(f"[CRUD Project] Found {len(projects)} projects.")
    return projects

async def get_project(db: AsyncSession, *, project_id: str) -> Optional[Project]:
    """Retrieve a single project by its ID."""
    logger.debug(f"[CRUD Project] Fetching project by ID: {project_id}")
    project = await db.get(Project, project_id)
    if project:
        logger.debug(f"[CRUD Project] Found project: {project.title}")
    else:
        logger.debug(f"[CRUD Project] Project with ID {project_id} not found.")
    return project

async def get_project_by_github_url(db: AsyncSession, *, github_url: str) -> Optional[Project]:
    """Retrieve a project by its GitHub URL."""
    logger.debug(f"[CRUD Project] Fetching project by GitHub URL: {github_url}")
    stmt = select(Project).where(Project.githubUrl == github_url)
    result = await db.execute(stmt)
    project = result.scalars().first()
    if project:
        logger.debug(f"[CRUD Project] Found project by GitHub URL: {project.title}")
    else:
        logger.debug(f"[CRUD Project] Project with GitHub URL {github_url} not found.")
    return project

async def get_project_by_title(db: AsyncSession, *, title: str) -> Optional[Project]:
    """Retrieve a project by its title."""
    logger.debug(f"[CRUD Project] Fetching project by title: {title}")
    stmt = select(Project).where(Project.title == title)
    result = await db.execute(stmt)
    project = result.scalars().first()
    if project:
        logger.debug(f"[CRUD Project] Found project by title: {project.title}")
    else:
        logger.debug(f"[CRUD Project] Project with title {title} not found.")
    return project

async def create_project(db: AsyncSession, *, project_in: ProjectCreate) -> Project:
    """Create a new project."""
    logger.debug(f"[CRUD Project] Creating new project: {project_in.title}")
    project_data = project_in.model_dump()
    if project_data.get("githubUrl") is not None:
        project_data["githubUrl"] = str(project_data["githubUrl"])
    if project_data.get("liveUrl") is not None:
        project_data["liveUrl"] = str(project_data["liveUrl"])
    if project_data.get("imageUrl") is not None:
        project_data["imageUrl"] = str(project_data["imageUrl"])
    if project_data.get("videoUrl") is not None:
        project_data["videoUrl"] = str(project_data["videoUrl"])

    db_obj = Project(**project_data)
    db.add(db_obj)
    try:
        await db.commit()
        await db.refresh(db_obj)
        logger.info(f"[CRUD Project] Project '{db_obj.title}' (ID: {db_obj.id}) created successfully.")
        return db_obj
    except Exception as e:
        await db.rollback()
        logger.error(f"[CRUD Project] Error creating project {project_in.title}: {e}", exc_info=True)
        raise

# async def update_project(...) -> Project:
#     ...

# async def delete_project(...) -> Project:
#     ... 