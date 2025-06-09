from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional

class SubmittedUrlBase(BaseModel):
    url: HttpUrl
    submission_type: Literal["news", "resource"]

class SubmittedUrlCreate(SubmittedUrlBase):
    pass

class SubmissionResponse(BaseModel):
    success: bool
    message: str
    item_id: Optional[str] = None
    star_rating: Optional[int] = None
    title: Optional[str] = None
    processed_url: Optional[HttpUrl] = None 