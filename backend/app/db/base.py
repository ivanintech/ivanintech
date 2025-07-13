# Este archivo ahora solo sirve para asegurar que los modelos
# sean importados y registrados por SQLAlchemy ANTES de que
# Alembic los necesite.

from app.db.base_class import Base

# Import all models from the models package.
# The order is controlled in app.db.models.__init__.py
from app.db import models  # noqa 