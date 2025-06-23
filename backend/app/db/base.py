# Este archivo ahora solo sirve para asegurar que los modelos
# sean importados y registrados por SQLAlchemy ANTES de que
# Alembic los necesite.

from .base_class import Base  # Importa la Base definida separadamente

# Importa todos tus modelos aquí para que se registren con Base.metadata
from app.db.models.user import User # noqa
from app.db.models.item import Item # noqa
from app.db.models.project import Project  # noqa
from app.db.models.blog_post import BlogPost # noqa
from app.db.models.news_item import NewsItem # noqa
from app.db.models.contact import ContactMessage # noqa
from app.db.models.resource_link import ResourceLink # noqa
from app.db.models.resource_vote import ResourceVote # noqa
from app.db.models.blog_suggestion import BlogSuggestion # noqa
from app.db.models.hero_media import HeroMedia # noqa
from app.db.models.about_media import AboutMedia # noqa

# Ya NO definimos la clase Base aquí
# class Base(DeclarativeBase):
#    ... 