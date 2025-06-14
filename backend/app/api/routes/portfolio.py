# app/api/routes/portfolio.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import logging # Import logging

from app.schemas.project import ProjectRead
# from app.db_mock import projects_db # No longer used
from app import crud # Import crud module
from app.db.session import get_db # Import session dependency

# Configure logger for this route
logger = logging.getLogger(__name__)

router = APIRouter()

# Convert the route to async
@router.get("/projects", response_model=List[ProjectRead])
async def read_projects(db: AsyncSession = Depends(get_db)):
    """Retrieve projects from the database asynchronously via CRUD layer."""
    logger.info("***** [API /projects] Endpoint reached *****") # Simple log
    try:
        projects = await crud.portfolio.get_projects(db=db)
        logger.info(f"***** [API /projects] CRUD returned: {len(projects)} projects *****") # Log with data count
        return projects
    except Exception as e:
        logger.error(f"***** [API /projects] Error fetching projects: {e} *****", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error fetching projects")

# Example of an endpoint for a single project (synchronous)
# @router.get("/projects/{project_id}", response_model=ProjectRead)
# def read_project(project_id: str, db: Session = Depends(get_db)):
#     db_project = crud.portfolio.get_project(db=db, project_id=project_id)
#     if db_project is None:
#         raise HTTPException(status_code=404, detail="Project not found")
#     return db_project

# We could add endpoints to get a project by ID, create, etc.
# async def read_project(id: str, db: AsyncSession = Depends(get_db)) -> ProjectRead:
#     db_project = await crud.get_project(db=db, id=id)
#     if not db_project:
#         raise HTTPException(status_code=404, detail="Project not found")
#     return db_project