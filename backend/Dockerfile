# Use a specific platform for build consistency
FROM --platform=${BUILDPLATFORM:-linux/amd64} python:3.10 AS base

# Install ca-certificates for secure database connections
# and other system dependencies.
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# Use a specific stage for getting the uv installer to keep the final image small
FROM --platform=${BUILDPLATFORM:-linux/amd64} ghcr.io/astral-sh/uv:0.5.11 AS uv

# Go back to the base image
FROM base

# Copy the uv installer from the uv stage
COPY --from=uv /uv /uvx /bin/

# Set working directory
WORKDIR /app
ENV PYTHONPATH=/app

# Create a virtual environment and add it to the PATH
RUN python -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency definition files
COPY pyproject.toml uv.lock alembic.ini ./

# Install dependencies into the virtual environment
RUN uv sync --no-install-project

# Copy the application source code
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./scripts ./scripts

# Make scripts executable
RUN chmod +x scripts/*.sh

# Install the project itself (if it's defined as a package)
RUN uv sync

# The CMD to run the application will be specified in the docker-compose file
