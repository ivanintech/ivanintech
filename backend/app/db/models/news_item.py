from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
# from sqlalchemy.dialects.sqlite import DATETIME # No es necesario si usamos DateTime(timezone=True)
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, List # Añadir List
import datetime
# from datetime import timezone # datetime ya lo importa
import uuid
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import TypeDecorator, CHAR

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
    title: Mapped[str] = mapped_column(String, index=True)
    # source = Column(String, index=True) # Columna antigua eliminada
    url: Mapped[str] = mapped_column(String, unique=True, index=True)
    # Usar DateTime(timezone=True) para asegurar información de zona horaria
    publishedAt: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.timezone.utc)) 
    description: Mapped[Optional[str]] = mapped_column(Text) # Usar Text para descripciones potencialmente largas
    imageUrl: Mapped[Optional[str]] = mapped_column(String(1024)) # Aumentar longitud por si acaso

    # Nuevos campos enriquecidos por IA (usando Mapped)
    relevance_score: Mapped[Optional[int]] = mapped_column(Integer)
    # time_category: Mapped[Optional[str]] = mapped_column(String) # Decidimos no usar este campo por ahora
    sectors: Mapped[Optional[List[str]]] = mapped_column(JSON) # Guardar lista como JSON

    # Nuevas columnas añadidas
    sourceName: Mapped[Optional[str]] = mapped_column(String(255)) # Nombre de la fuente API/Scraping
    sourceId: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # ID de la fuente si lo proporciona la API

    # Campos renombrados/eliminados (solo como referencia):
    # summary: Mapped[Optional[str]] = mapped_column(Text) # -> Usamos description
    # published_date = Column(String) # Migrado a publishedAt (DateTime)
    # image_url = Column(String) # Migrado a imageUrl

    # Additional columns
    relevance_score: Mapped[Optional[int]] = mapped_column(Integer)
    time_category: Mapped[Optional[str]] = mapped_column(String)
    sectors: Mapped[Optional[dict]] = mapped_column(JSON) 