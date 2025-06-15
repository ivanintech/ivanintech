FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --system --no-install-project

# Copy the rest of the application code
COPY alembic.ini .
COPY app ./app
COPY scripts ./scripts

# Sync the project itself
RUN uv sync --system

ENV PYTHONPATH=/app

# The command to run the application in production
# Render will automatically set the PORT environment variable. Uvicorn will use it.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
