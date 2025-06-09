from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional
import uuid
from datetime import datetime

from app.db.base_class import Base # Asegúrate que la importación de Base sea correcta según tu estructura

class ResourceLink(Base):
    __tablename__ = "resource_links"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True, default=lambda: uuid.uuid4().hex)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False) # Aumentado el límite para URLs largas
    ai_generated_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personal_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True) # Ej: Video, GitHub, Artículo
    tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True) # Comma-separated tags
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    star_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # New field for star rating
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now) # Usar func.now sin paréntesis para que se ejecute en la BD
    # last_modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=func.now, onupdate=func.now) # Opcional

    # Si quieres asociar un autor (quién añadió el recurso):
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), nullable=True) # O False si es obligatorio
    author: Mapped["User"] = relationship("User", back_populates="resource_links") # Necesitarías añadir "resource_links = relationship("ResourceLink")" en User model

    # Para la funcionalidad de fijar
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    def __repr__(self):
        return f"<ResourceLink(title='{self.title}', url='{self.url}')>" 