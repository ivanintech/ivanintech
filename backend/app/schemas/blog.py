from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
import datetime # Importar datetime completo para date

# Shared properties
class BlogPostBase(BaseModel):
    title: str
    # slug: str # Se generará a partir del título en el backend
    content: str
    excerpt: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[HttpUrl | str] = None 
    linkedin_post_url: Optional[HttpUrl | str] = None
    status: str = 'published'
    # published_date se establecerá en el backend

# Properties to receive on item creation
class BlogPostCreate(BlogPostBase):
    # id se generará en el backend
    # author_id se tomará del usuario autenticado
    # slug se generará del título
    # published_date se establecerá en el backend
    # Solo se necesita el contenido que viene de BlogPostBase y que el cliente debe proveer
    pass # Todos los campos necesarios ya están en BlogPostBase

# Properties to receive on item update
class BlogPostUpdate(BaseModel): 
    title: Optional[str] = None
    # slug: Optional[str] = None # Actualizar slug puede ser complejo, considerar si es necesario
    content: Optional[str] = None
    excerpt: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[HttpUrl | str] = None
    linkedin_post_url: Optional[HttpUrl | str] = None
    status: Optional[str] = None

# Properties returned to client
class BlogPostRead(BlogPostBase): 
    id: str 
    author_id: int
    slug: str # Devolver el slug generado
    published_date: datetime.date 
    last_modified_date: Optional[datetime.date] = None

    class Config:
        from_attributes = True