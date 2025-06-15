from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime
import uuid
import json

# Schema base para compartir atributos comunes
class NewsItemBase(BaseModel):
    title: Optional[str] = None # Hacer opcional para Update
    # source: Optional[str] = None # Campo antiguo, parece reemplazado
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    imageUrl: Optional[HttpUrl] = None
    # Nuevos campos
    relevance_score: Optional[int] = None
    # time_category: Optional[str] = None # Este campo no parece usarse ya
    sectors: Optional[List[str]] = None
    publishedAt: Optional[datetime] = None 
    # Añadir campos que faltaban y que usa el CRUD
    sourceName: Optional[str] = None 
    sourceId: Optional[str] = None 
    star_rating: Optional[float] = Field(None, ge=1.0, le=5.0) # Calificación 1-5 estrellas (float)
    is_community: Optional[bool] = False

# Schema para crear un nuevo item (requiere título y url)
class NewsItemCreate(NewsItemBase):
    title: str # Sobrescribir para que sea requerido
    url: HttpUrl # Sobrescribir para que sea requerido
    # Los demás son opcionales y vienen de Base
    # sourceName y sourceId son opcionales
    sourceName: Optional[str] = None # Asegurar que se incluya en la lectura
    sourceId: Optional[str] = None # Asegurar que se incluya en la lectura
    star_rating: Optional[float] = Field(None, ge=1.0, le=5.0)

    @field_validator('sectors', mode='before')
    @classmethod
    def parse_sectors_from_json_string(cls, value: Union[str, List[str], None]) -> Optional[List[str]]:
        if isinstance(value, str):
            try:
                # Attempt to parse the string as JSON
                parsed_value = json.loads(value)
                if isinstance(parsed_value, list):
                    return parsed_value
                return None # Or raise an error if it's not a list after parsing
            except json.JSONDecodeError:
                # If it's not valid JSON, or not the expected list type, return None or handle as error
                # This might occur if the string is not a JSON array, e.g. "{Finanzas,Robótica}"
                # For now, we'll assume if it's a string, it should be a JSON list string
                return None 
        return value # If it's already a list or None, return as is

# Schema para actualizar un item (todos los campos opcionales)
class NewsItemUpdate(NewsItemBase):
    pass # Hereda todos los campos opcionales de Base

# Schema para leer/retornar un item
class NewsItemRead(NewsItemBase):
    id: uuid.UUID # Cambiado de int a uuid.UUID si corresponde
    title: str # Asegurar que title no sea opcional al leer
    url: HttpUrl # Asegurar que url no sea opcional al leer
    publishedAt: datetime # Asegurar que publishedAt no sea opcional al leer
    # Los demás campos pueden ser Optional según la base
    sourceName: Optional[str] = None # Asegurar que se incluya en la lectura
    sourceId: Optional[str] = None # Asegurar que se incluya en la lectura
    star_rating: Optional[float] = Field(None, ge=1.0, le=5.0)

    @field_validator('sectors', mode='before')
    @classmethod
    def parse_sectors_from_json_string(cls, value: Union[str, List[str], None]) -> Optional[List[str]]:
        if isinstance(value, str):
            try:
                # Attempt to parse the string as JSON
                parsed_value = json.loads(value)
                if isinstance(parsed_value, list):
                    return parsed_value
                return None # Or raise an error if it's not a list after parsing
            except json.JSONDecodeError:
                # If it's not valid JSON, or not the expected list type, return None or handle as error
                # This might occur if the string is not a JSON array, e.g. "{Finanzas,Robótica}"
                # For now, we'll assume if it's a string, it should be a JSON list string
                return None 
        return value # If it's already a list or None, return as is

    class Config:
        from_attributes = True # Reemplazo de orm_mode 