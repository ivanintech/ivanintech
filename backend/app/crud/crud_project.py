from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.models.project import Project
# from app.schemas.project import ProjectCreate, ProjectUpdate # Para futuras operaciones CUD

async def get_projects(db: AsyncSession) -> List[Project]:
    """Retrieve all projects from the database."""
    result = await db.execute(select(Project).order_by(Project.title)) # Ordenar por título, por ejemplo
    return result.scalars().all()

# --- Funciones Create, Update, Delete (a implementar si son necesarias) ---
# async def create_project(db: AsyncSession, *, obj_in: ProjectCreate) -> Project:
#     db_obj = Project(**obj_in.model_dump())
#     db.add(db_obj)
#     await db.commit()
#     await db.refresh(db_obj)
#     return db_obj

# async def get_project(db: AsyncSession, id: str) -> Project | None:
#     return await db.get(Project, id)

# async def update_project(...) -> Project:
#     ...

# async def delete_project(...) -> Project:
#     ... 