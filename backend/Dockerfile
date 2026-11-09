# Usar una imagen oficial y ligera de Python
FROM python:3.10-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalar uv, nuestro gestor de paquetes
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Crear un entorno virtual y añadirlo al PATH
RUN python -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Copiar archivos de dependencias y de configuración
COPY pyproject.toml uv.lock alembic.ini ./

# Instalar las dependencias
RUN uv sync --no-install-project

# Copiar el código de la aplicación y los scripts de migración
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./scripts ./scripts

# Dar permiso de ejecución al script de arranque (llega sin +x desde git en algunos sistemas)
RUN chmod +x ./scripts/prestart.sh

# Instalar la propia aplicación en el entorno virtual
RUN uv sync

# Comando para ejecutar la aplicación.
#
# IMPORTANTE: el arranque pasa por scripts/prestart.sh, NO por `alembic upgrade head`
# directo. El prestart comprueba si ya existe una BD migrada y, en tal caso, omite
# las migraciones. Migrar a pelo sobre la BD restaurada rompe el arranque con
# KeyError porque su alembic_version (e38e15120cf7) no existe en alembic/versions/
# (esto causó el deploy fallido del 8-nov-2026).
CMD ["./scripts/prestart.sh"]
