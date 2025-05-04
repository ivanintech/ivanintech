from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

# Shared properties
class BlogPostBase(BaseModel):
    title: str
    slug: str
    content: str
    tags: Optional[str] = None
    image_url: Optional[HttpUrl | str] = None
    linkedin_post_url: Optional[HttpUrl | str] = None
    status: str = 'published'

# Properties to receive on item creation
class BlogPostCreate(BlogPostBase):
    pass

# Properties to receive on item update
class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None
    image_url: Optional[HttpUrl | str] = None
    linkedin_post_url: Optional[HttpUrl | str] = None
    status: Optional[str] = None

# Properties returned to client
class BlogPostRead(BlogPostBase):
    id: str
    author_id: int
    published_date: datetime # Nota: Si 'published_date' fuera date y no datetime, cambiar aquí también.
    last_modified_date: Optional[datetime] = None

    class Config:
        orm_mode = True # Cambiar a from_attributes si usas Pydantic v2