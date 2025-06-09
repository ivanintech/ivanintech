import uuid # Import uuid
from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from typing import List, Optional

from app.db.base_class import Base

class Project(Base):
    __tablename__ = "projects"

    # id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    # Using string representation of UUID for broader compatibility (e.g. SQLite)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    # Usamos JSON para almacenar la lista de tecnologías
    # SQLite soporta JSON de forma nativa
    technologies: Mapped[List[str]] = mapped_column(JSON)
    imageUrl: Mapped[Optional[str]] = mapped_column(String(500))
    videoUrl: Mapped[Optional[str]] = mapped_column(String(500))
    githubUrl: Mapped[Optional[str]] = mapped_column(String(500))
    liveUrl: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # created_at, updated_at si los tienes 