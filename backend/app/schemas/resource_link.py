from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime
import uuid # Para el default_factory del ID en el schema si es necesario

# Shared properties
class ResourceLinkBase(BaseModel):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    ai_generated_description: Optional[str] = None
    personal_note: Optional[str] = None
    resource_type: Optional[str] = None
    tags: Optional[str] = None # Comma-separated string
    thumbnail_url: Optional[HttpUrl] = None
    star_rating: Optional[int] = Field(None, ge=1, le=5) # Calificación 1-5 estrellas

# Properties to receive on item creation
class ResourceLinkCreate(ResourceLinkBase):
    title: Optional[str] = None # El título ahora es opcional, será generado por Gemini
    url: HttpUrl # La URL sigue siendo obligatoria al crear desde el formulario
    # ai_generated_description, personal_note y thumbnail_url serán generados/opcionales al crear desde la API

# Properties to receive on item update
class ResourceLinkUpdate(ResourceLinkBase):
    pass # Todos los campos son opcionales para la actualización

# Properties shared by models stored in DB
class ResourceLinkInDBBase(ResourceLinkBase):
    id: str # Usar str para el ID ya que es un UUID hex
    title: str
    url: str # En la BD se almacena como string
    thumbnail_url: Optional[str] = None # En la BD se almacena como string
    star_rating: Optional[int] = Field(None, ge=1, le=5) # Ensure it's here too for DB model mapping
    created_at: datetime
    author_id: Optional[int] = None # Nuevo campo
    is_pinned: bool = False # Nuevo campo, con default

    class Config:
        from_attributes = True # Reemplaza orm_mode

# Additional properties to return to client (API output)
class ResourceLinkRead(ResourceLinkInDBBase):
    author_name: Optional[str] = None # Para mostrar el nombre del autor
    # is_pinned ya está heredado de ResourceLinkInDBBase y su default es False
    pass

# Podríamos tener un schema para el objeto tal cual está en la BD si es necesario, pero Read suele ser suficiente.
# class ResourceLinkInDB(ResourceLinkInDBBase):
#     pass 