from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID

# --- Base Schema ---
class BlogSuggestionBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    source: Optional[str] = None
    status: str = 'pending'

# --- Schema for Creation ---
class BlogSuggestionCreate(BlogSuggestionBase):
    title: str
    content: str

# --- Schema for Updating ---
class BlogSuggestionUpdate(BlogSuggestionBase):
    pass

# --- Schema for Reading from DB ---
class BlogSuggestionInDBBase(BlogSuggestionBase):
    id: str # Debería ser str para coincidir con el modelo UUID
    created_at: datetime
    processed_at: Optional[datetime] = None
    published_post_id: Optional[str] = None # Debería ser str

    class Config:
        from_attributes = True

# --- Public-facing Read Schema ---
class BlogSuggestionRead(BlogSuggestionInDBBase):
    pass 