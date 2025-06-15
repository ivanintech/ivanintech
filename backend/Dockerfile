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

# Instalar la propia aplicación en el entorno virtual
RUN uv sync

# Comando para ejecutar la aplicación.
# Fuerza un reseteo de la BD a un estado limpio y luego aplica todas las migraciones.
CMD alembic downgrade base && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
