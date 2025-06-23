from sqlalchemy import Column, Integer, String, Boolean
from app.db.base_class import Base

class AboutMedia(Base):
    __tablename__ = "about_media"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    media_url = Column(String, nullable=False, unique=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True) 