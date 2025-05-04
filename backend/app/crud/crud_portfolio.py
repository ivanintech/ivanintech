from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.db.models.project import Project
# Podríamos necesitar el schema si devolvemos un tipo específico o validamos,
# pero para un get simple, el modelo suele bastar.
# from app.schemas.project import ProjectRead 
from app.schemas.project import ProjectCreate, ProjectUpdate


async def get_projects(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Project]:
    """Obtiene una lista de proyectos."""
    # Log al inicio de la función CRUD
    print(f"[crud_portfolio.get_projects] Recibida sesión ({type(db)}), bind: {db.bind}")
    stmt = select(Project).order_by(Project.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_project(db: AsyncSession, *, project_in: ProjectCreate) -> Project:
    """Crea un nuevo proyecto."""
    # Convertir datos del schema a un diccionario
    project_data = project_in.model_dump()
    
    # --- CORRECCIÓN: Convertir HttpUrl a string antes de crear el modelo --- #
    if project_data.get("githubUrl") is not None:
        project_data["githubUrl"] = str(project_data["githubUrl"])
    if project_data.get("liveUrl") is not None:
        project_data["liveUrl"] = str(project_data["liveUrl"])
    # --- FIN CORRECCIÓN ---
    
    # Crear la instancia del modelo SQLAlchemy usando el diccionario modificado
    db_project = Project(**project_data)
    
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

async def get_project(db: AsyncSession, project_id: str) -> Optional[Project]:
    """Obtiene un proyecto por su ID."""
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    return result.scalars().first()

# Aquí podríamos añadir funciones CRUD adicionales en el futuro:
# async def get_project(db: AsyncSession, project_id: str) -> Project | None:
#     result = await db.execute(select(Project).filter(Project.id == project_id))
#     return result.scalars().first()
#
# def update_project(...)
# def delete_project(...) 