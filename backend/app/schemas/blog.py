from pydantic import BaseModel, HttpUrl, Field, computed_field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

from .user import User

class BlogPostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

# Author schema for nested responses
class Author(BaseModel):
    id: int
    full_name: Optional[str] = "Ivan"

    class Config:
        from_attributes = True

# Shared properties
class BlogPostBase(BaseModel):
    title: str
    # slug: str # Se generará a partir del título en el backend
    content: str
    excerpt: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[HttpUrl | str] = None
    linkedin_post_url: Optional[HttpUrl | str] = None
    status: Optional[str] = 'published'
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
    # No permitir la actualización directa de author_id o slug aquí

# Properties shared by models stored in DB
class BlogPostInDBBase(BlogPostBase):
    id: str
    author_id: int
    slug: str
    published_date: date
    last_modified_date: Optional[date] = None
    # El campo 'author' es para las respuestas al cliente, no para la base de datos
    # author: User # Usar User aquí para la relación

    class Config:
        from_attributes = True


# Properties returned to client
class BlogPostRead(BlogPostInDBBase):
    author: Author # Usar el esquema de autor simplificado para la respuesta

    @computed_field
    @property
    def url(self) -> str:
        return f"/blog/{self.slug}"

# Properties to return to client in a list
class BlogPostList(BaseModel):
    items: List[BlogPostRead]