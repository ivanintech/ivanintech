from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ARRAY, Float
# from sqlalchemy.dialects.sqlite import DATETIME # No es necesario si usamos DateTime(timezone=True)
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List, Any # Añadir List y Any
import datetime
# from datetime import timezone # datetime ya lo importa
import uuid
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB # Opcional, si usas PostgreSQL y quieres JSONB

from app.db.base_class import Base

# --- UUID Handling --- #
class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PGUUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value
# --- End UUID Handling --- #

class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    # source = Column(String, index=True) # Columna antigua eliminada
    url: Mapped[str] = mapped_column(String(2048), unique=True, index=True, nullable=False)
    # Usar DateTime(timezone=True) para asegurar información de zona horaria
    publishedAt: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    imageUrl: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    # Nuevos campos enriquecidos por IA (usando Mapped)
    relevance_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # time_category: Mapped[Optional[str]] = mapped_column(String) # Decidimos no usar este campo por ahora
    sectors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Nuevas columnas añadidas
    sourceName: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sourceId: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Campos de análisis de Gemini
    # time_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # ej: 'Hoy', 'Semana', 'Mes' (Ya no lo necesitamos, lo calcularemos on-the-fly o al mostrar)
    # relevance_score: Mapped[Optional[int]] = mapped_column(Integer)
    # sectors: Mapped[Optional[dict]] = mapped_column(JSON)

    # Nuevo campo para la calificación de estrellas (1-5)
    star_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Campos de timestamps automáticos (opcional pero útil)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<NewsItem(title='{self.title[:50]}...', sourceName='{self.sourceName}', publishedAt='{self.publishedAt}')>"

    # Campos renombrados/eliminados (solo como referencia):
    # summary: Mapped[Optional[str]] = mapped_column(Text) # -> Usamos description
    # published_date = Column(String) # Migrado a publishedAt (DateTime)
    # image_url = Column(String) # Migrado a imageUrl

    # REMOVE THE FOLLOWING DUPLICATED/OBSOLETE Additional columns:
    # relevance_score: Mapped[Optional[int]] = mapped_column(Integer)
    # time_category: Mapped[Optional[str]] = mapped_column(String)
    # sectors: Mapped[Optional[dict]] = mapped_column(JSON) 