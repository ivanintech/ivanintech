import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional, TYPE_CHECKING
from app.db.base_class import Base
from sqlalchemy.sql import func
from app.core.config import settings

if TYPE_CHECKING:
    from .news_item import NewsItem
    from .resource_vote import ResourceVote

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True) # Mantenemos Integer según migración inicial
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_path: Mapped[Optional[str]] = mapped_column("avatar_url", String(512), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_login_at = Column(DateTime, nullable=True)

    # Relación con BlogPost
    blog_posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")

    # Relación inversa con NewsItem
    submitted_news = relationship("NewsItem", back_populates="submitted_by")

    # Relación con ResourceLink
    resource_links: Mapped[List["ResourceLink"]] = relationship("ResourceLink", back_populates="author", cascade="all, delete-orphan")

    # --- Relación con los votos ---
    resource_votes = relationship("ResourceVote", back_populates="user")

    # Relación (si se usa Item):
    # items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")

    @property
    def avatar_url(self) -> Optional[str]:
        if self.avatar_path:
            # Asegurarse de que no haya una doble barra
            base_url = str(settings.SERVER_HOST).rstrip('/')
            avatar_path = self.avatar_path.lstrip('/')
            return f"{base_url}/{avatar_path}"
        return None

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', is_superuser={self.is_superuser})>" 