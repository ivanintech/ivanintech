from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import logging

from app.db.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.crud.base import CRUDBase

logger = logging.getLogger(__name__)


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[Project]:
        """
        Retrieve multiple projects, ordered by featured status and then title.
        """
        result = await db.execute(
            select(self.model)
            .order_by(self.model.is_featured.desc(), self.model.title)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_title(self, db: AsyncSession, *, title: str) -> Optional[Project]:
        statement = select(self.model).where(self.model.title == title)
        return (await db.execute(statement)).scalars().first()

    async def get_by_github_url(self, db: AsyncSession, *, github_url: str) -> Optional[Project]:
        statement = select(self.model).where(self.model.githubUrl == github_url)
        return (await db.execute(statement)).scalars().first()

    async def toggle_featured(self, db: AsyncSession, *, project_id: str) -> Optional[Project]:
        """Toggles the is_featured status of a project."""
        db_obj = await self.get(db=db, id=project_id)
        if not db_obj:
            return None
        
        updated_data = ProjectUpdate(is_featured=not db_obj.is_featured)
        return await super().update(db=db, db_obj=db_obj, obj_in=updated_data)

    # The generic `create`, `update`, `remove`, and `get` methods from CRUDBase are inherited
    # and can be used directly. No need to redefine them here unless you need
    # custom logic (like hashing a password for users).


project = CRUDProject(Project)

# async def get_project(db: AsyncSession, *, project_id: str) -> Optional[Project]:
#     """Retrieve a single project by its ID."""
#     logger.debug(f"[CRUD Project] Fetching project by ID: {project_id}")
#     project = await db.get(Project, project_id)
#     if project:
#         logger.debug(f"[CRUD Project] Found project: {project.title}")
#     else:
#         logger.debug(f"[CRUD Project] Project with ID {project_id} not found.")
#     return project

# async def get_project_by_title(db: AsyncSession, *, title: str) -> Optional[Project]:
#     ...

# async def create_project(db: AsyncSession, *, project_in: ProjectCreate) -> Project:
#     """Create a new project."""
#     logger.debug(f"[CRUD Project] Creating new project: {project_in.title}")
#     project_data = project_in.model_dump()
#     if project_data.get("githubUrl") is not None:
#         project_data["githubUrl"] = str(project_data["githubUrl"])
#     if project_data.get("liveUrl") is not None:
#         project_data["liveUrl"] = str(project_data["liveUrl"])
#     if project_data.get("imageUrl") is not None:
#         project_data["imageUrl"] = str(project_data["imageUrl"])
#     if project_data.get("videoUrl") is not None:
#         project_data["videoUrl"] = str(project_data["videoUrl"])
#
#     db_obj = Project(**project_data)
#     db.add(db_obj)
#     try:
#         await db.commit()
#         await db.refresh(db_obj)
#         logger.info(f"[CRUD Project] Project '{db_obj.title}' (ID: {db_obj.id}) created successfully.")
#         return db_obj
#     except Exception as e:
#         await db.rollback()
#         logger.error(f"[CRUD Project] Error creating project {project_in.title}: {e}", exc_info=True)
#         raise

# async def update_project(...) -> Project:
#     ...

# async def delete_project(...) -> Project:
#     ... 