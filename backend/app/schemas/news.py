from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime
import uuid
import json

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
    relevance_rating: Optional[int] = Field(None, ge=1, le=5) # Calificación 1-5 estrellas

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
    title: str
    url: HttpUrl
    publishedAt: datetime

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