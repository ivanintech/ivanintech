from pydantic import BaseModel
from typing import Optional

# Shared properties
class HeroMediaBase(BaseModel):
    name: str
    media_type: str
    media_url: str
    order: Optional[int] = 0
    is_active: Optional[bool] = True

# Properties to receive on item creation
class HeroMediaCreate(HeroMediaBase):
    pass

# Properties to receive on item update
class HeroMediaUpdate(HeroMediaBase):
    pass

# Properties shared by models stored in DB
class HeroMediaInDBBase(HeroMediaBase):
    id: int

    class Config:
        orm_mode = True

# Properties to return to client
class HeroMedia(HeroMediaInDBBase):
    pass

# Properties stored in DB
class HeroMediaInDB(HeroMediaInDBBase):
    pass 