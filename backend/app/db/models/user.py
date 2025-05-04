from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True) # Mantenemos Integer según migración inicial
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)

    # Relación con BlogPost
    blog_posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")

    # Relación (si se usa Item):
    # items = relationship("Item", back_populates="owner", cascade="all, delete-orphan") 