from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime
import uuid
import json
from .user import UserPublic

# Schema base para compartir atributos comunes
class NewsItemBase(BaseModel):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    imageUrl: Optional[HttpUrl] = None
    sectors: Optional[List[str]] = None
    publishedAt: Optional[datetime] = None 
    sourceName: Optional[str] = None 
    sourceId: Optional[str] = None 
    is_community: Optional[bool] = False
    relevance_rating: Optional[float] = Field(None, ge=0.0, le=5.0) # Calificación 0.0-5.0
    submitted_by_user_id: Optional[int] = None

# Schema para la subida de una noticia por parte de un usuario (solo URL)
class NewsItemSubmit(BaseModel):
    url: HttpUrl

# Schema para crear un nuevo item (requiere título y url)
class NewsItemCreate(NewsItemBase):
    title: str
    url: HttpUrl
    # Los demás son opcionales y vienen de Base

    @field_validator('sectors', mode='before')
    @classmethod
    def parse_sectors_from_json_string(cls, value: Union[str, List[str], None]) -> Optional[List[str]]:
        if isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                if isinstance(parsed_value, list):
                    return parsed_value
                return None
            except json.JSONDecodeError:
                return None 
        return value

# Schema para actualizar un item (todos los campos opcionales)
class NewsItemUpdate(NewsItemBase):
    pass

# Schema para leer/retornar un item
class NewsItemRead(NewsItemBase):
    id: uuid.UUID
    is_community: Optional[bool] = False
    relevance_rating: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    submitted_by: Optional[UserPublic] = None
    promotion_level: int = 0 # 0: normal, 1: >3.5, 2: >4.0 + top 20%

    @field_validator('sectors', mode='before')
    @classmethod
    def parse_sectors_from_json_string(cls, value: Union[str, List[str], None]) -> Optional[List[str]]:
        if isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                if isinstance(parsed_value, list):
                    return parsed_value
                return None
            except json.JSONDecodeError:
                return None 
        return value

    class Config:
        from_attributes = True 

# Properties to return to client
class NewsItem(NewsItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    submitted_by: Optional[UserPublic] = None 

    class Config:
        orm_mode = True 