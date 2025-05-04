from pydantic import BaseModel, HttpUrl
from typing import List, Optional

# Esquema base para propiedades comunes
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = []
    imageUrl: Optional[str] = None
    videoUrl: Optional[str] = None
    githubUrl: Optional[HttpUrl] = None
    liveUrl: Optional[HttpUrl] = None

# Esquema para la creación de un proyecto
# Hereda de la base, los campos son los mismos requeridos/opcionales que la base
class ProjectCreate(ProjectBase):
    pass

# Esquema para actualizar un proyecto
# Hereda de la base, pero todos los campos son opcionales
class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    imageUrl: Optional[str] = None
    videoUrl: Optional[str] = None
    githubUrl: Optional[HttpUrl] = None
    liveUrl: Optional[HttpUrl] = None

# Esquema para leer un proyecto (desde la API)
# Incluye el ID y hereda de la base
class ProjectRead(ProjectBase):
    id: str

    # Configuración para permitir mapeo desde modelos ORM (si usamos DB)
    class Config:
        orm_mode = True # En Pydantic v2 se llama from_attributes=True 