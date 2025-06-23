from pydantic import BaseModel
from typing import Optional

class AboutMediaBase(BaseModel):
    name: str
    media_url: str
    order: Optional[int] = 0
    is_active: Optional[bool] = True

class AboutMediaCreate(AboutMediaBase):
    pass

class AboutMediaUpdate(AboutMediaBase):
    pass

class AboutMediaInDBBase(AboutMediaBase):
    id: int
    class Config:
        orm_mode = True

class AboutMedia(AboutMediaInDBBase):
    pass 