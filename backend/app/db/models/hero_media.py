from sqlalchemy import Column, Integer, String, Boolean
from app.db.base_class import Base

class HeroMedia(Base):
    __tablename__ = "hero_media"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    media_type = Column(String, nullable=False)  # 'image' or 'video'
    media_url = Column(String, nullable=False)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True) 