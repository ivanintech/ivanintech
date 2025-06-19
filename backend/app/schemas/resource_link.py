from pydantic import BaseModel, HttpUrl, Field, computed_field
from typing import Optional, Any
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
    created_at: Optional[datetime] = None # Permitir pasar la fecha de creación
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
    star_rating: Optional[float] = Field(None, ge=1, le=5)
    created_at: datetime
    author_id: Optional[int] = None
    is_pinned: bool = False
    likes: int = 0
    dislikes: int = 0
    author: Optional[Any] = Field(None, exclude=True) # Cargar la relación pero excluirla del output
    
    class Config:
        from_attributes = True

# Additional properties to return to client (API output)
class ResourceLinkRead(ResourceLinkInDBBase):

    @computed_field
    @property
    def author_name(self) -> Optional[str]:
        if self.author and hasattr(self.author, 'full_name'):
            return self.author.full_name
        return None

# Podríamos tener un schema para el objeto tal cual está en la BD si es necesario, pero Read suele ser suficiente.
# class ResourceLinkInDB(ResourceLinkInDBBase):
#     pass 

class ResourceLinkVoteResponse(BaseModel):
    message: str
    resource: Optional[ResourceLinkRead] = None