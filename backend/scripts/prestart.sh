#! /usr/bin/env bash

# Exit in case of error
set -e

# ---------------------------------------------------------------------------
# Migraciones de Alembic: solo sobre BD nueva o vacia.
#
# Por que: la BD de produccion restaurada (ivanintech.db) tiene su propio
# alembic_version (e38e15120cf7) que YA NO EXISTE en el repo: la cadena de
# migraciones del proyecto divergio de su snapshot. Ejecutar
# `alembic upgrade head` sobre ella falla con KeyError y tumba el arranque
# (esto es lo que rompio el deploy del 8-nov-2026 en Render).
#
# La ruta del fichero depende del bind mount del docker-compose:
#   - En Render (contenedor efimero) no hay mount -> la BD no persiste ahi.
#   - En local (docker-compose.override.yml) se monta en /app/app/ivanintech.db
#     y la app resuelve `sqlite:///./ivanintech.db` relativo a su CWD (/app/app).
#
# Comprobamos las dos rutas para no migrar nunca sobre datos vivos.
# Variable opcional DB_PATH para forzar una ruta concreta.
# ---------------------------------------------------------------------------
DB_CANDIDATES=(
  "${DB_PATH:-}"
  "/app/app/ivanintech.db"
  "/app/ivanintech.db"
)

echo "--- Prestart: buscando base de datos existente ---"
DB_FOUND=""
for candidate in "${DB_CANDIDATES[@]}"; do
  if [ -n "$candidate" ] && [ -f "$candidate" ]; then
    DB_FOUND="$candidate"
    break
  fi
done

if [ -n "$DB_FOUND" ]; then
  echo "--- BD encontrada en $DB_FOUND (ya migrada/poblada). Se omiten las migraciones. ---"
  # Solo informamos de la version, nunca migramos sobre datos vivos.
  if command -v sqlite3 >/dev/null 2>&1; then
    VERSION=$(sqlite3 "$DB_FOUND" "select version_num from alembic_version;" 2>/dev/null || echo "sin-tabla")
    echo "--- alembic_version en la BD: $VERSION ---"
    echo "--- NOTA: las migraciones del repo no tienen por que incluir esta revision. ---"
  fi
else
  # -------------------------------------------------------------------------
  # Sin fichero SQLite: puede ser Postgres (Neon/Supabase) via DATABASE_URL.
  # Si esa BD YA tiene tablas de negocio, esta poblada y no hay que migrar:
  # su alembic_version puede no existir en el repo (cadena divergente) y
  # `alembic upgrade head` tumbaria el arranque.
  # Si esta vacia, si migramos (BD nueva de verdad).
  # -------------------------------------------------------------------------
  PG_POPULATED=""
  if [ -n "${DATABASE_URL:-}" ]; then
    # asyncpg usa `ssl=require`; psycopg (el que usa alembic) necesita `sslmode=require`.
    PG_URL=$(printf '%s' "$DATABASE_URL" | sed 's|postgresql+asyncpg://|postgresql://|; s|[?&]ssl=|?sslmode=|')
    TABLES=$(python3 - "$PG_URL" <<'PY' 2>/dev/null || echo ""
import sys
try:
    import psycopg
    with psycopg.connect(sys.argv[1], connect_timeout=10) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from information_schema.tables where table_schema='public'")
            print(cur.fetchone()[0])
except Exception:
    print("")
PY
)
    if [ -n "$TABLES" ] && [ "$TABLES" -gt 0 ] 2>/dev/null; then
      PG_POPULATED="yes"
      echo "--- Postgres detectado con $TABLES tablas en 'public'. Se omiten las migraciones. ---"
    else
      echo "--- Postgres detectado pero vacio (o inaccesible: '$TABLES'). ---"
    fi
  fi

  if [ -z "$PG_POPULATED" ]; then
    echo "--- No hay BD previa. Ejecutando migraciones de Alembic ---"
    alembic upgrade head
  fi
fi

echo "--- Prestart script finalizado. Arrancando la aplicacion... ---"

# Arrancar uvicorn en primer plano (PID 1 del contenedor).
# exec sustituye el proceso para que las señales (SIGTERM de Render) lleguen a uvicorn
# y el apagado sea limpio en vez de forzar un kill.
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}"
