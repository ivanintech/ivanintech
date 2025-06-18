#! /usr/bin/env bash

# Exit in case of error
set -e

# Run alembic migrations to create/update database tables
echo "--- Running Alembic migrations ---"
alembic upgrade head

echo "--- Prestart script finished. Database migrations are up to date. App will handle data seeding. ---"
