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

# Copiar solo los archivos de definición de dependencias
COPY pyproject.toml uv.lock ./

# Instalar las dependencias en el entorno virtual.
# Esta capa solo se reconstruye si pyproject.toml o uv.lock cambian.
RUN uv sync --no-install-project

# Copiar el resto del código fuente de la aplicación
COPY alembic.ini .
COPY app ./app
COPY scripts ./scripts

# Instalar la propia aplicación en el entorno virtual
RUN uv sync

# Comando para ejecutar la aplicación en producción.
# Render establece automáticamente la variable de entorno PORT, que Uvicorn usará.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
