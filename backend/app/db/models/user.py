import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from app.db.base_class import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True) # Mantenemos Integer según migración inicial
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.now)
    last_login_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relación con BlogPost
    blog_posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")

    # Relación con ResourceLink
    resource_links: Mapped[List["ResourceLink"]] = relationship("ResourceLink", back_populates="author", cascade="all, delete-orphan")

    # Relación (si se usa Item):
    # items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")

    # --- Relación con los votos ---
    votes: Mapped[List["ResourceVote"]] = relationship("ResourceVote", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', is_superuser={self.is_superuser})>" 