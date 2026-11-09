#!/usr/bin/env python3
"""Importa a Neon los news_items que solo existen en la BD local (SQLite).

Por qué existe: la BD local tiene 797 noticias y Neon solo 302. Esta script
compara por URL (no por id, porque local usa hex de 32 chars y Neon uuid con
guiones), e inserta únicamente las 495 que faltan.

Modo por defecto: DRY RUN (no escribe nada). Con --apply sí inserta.
"""
import sqlite3
import subprocess
import sys
import json
import uuid
import os
import csv

LOCAL_DB = "ivanintech.db"
COLUMNS = [
    "id", "title", "url", "publishedAt", "description", "imageUrl",
    "relevance_rating", "sectors", "sourceName", "sourceId",
    "created_at", "updated_at", "is_community", "submitted_by_user_id",
]


def neon_dsn() -> str:
    """Lee la DSN desde ~/.secrets, sin dejarla en la línea de comandos."""
    path = os.path.expanduser("~/.secrets/neon-ivanintech.txt")
    with open(path) as fh:
        for line in fh:
            if line.startswith("DATABASE_URL="):
                dsn = line.split("=", 1)[1].strip()
                return dsn.replace("postgresql+asyncpg://", "postgresql://")
    raise SystemExit("No encontré DATABASE_URL en ~/.secrets/neon-ivanintech.txt")


def to_uuid(raw: str) -> str:
    """Convierte el id hex de 32 chars de SQLite a uuid con guiones."""
    raw = (raw or "").strip()
    if len(raw) == 32 and "-" not in raw:
        return str(uuid.UUID(raw))
    return str(uuid.UUID(raw))


def norm_sectors(value):
    """sectors viene como JSON en SQLite; puede ser NULL, lista o dict."""
    if value in (None, "", "null"):
        return "[]"
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    try:
        json.loads(value)  # valida
        return value
    except Exception:
        return "[]"


def clean(value):
    """None / strings vacíos → NULL para que Postgres no confunda tipos."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def rating(value):
    """relevance_rating es INTEGER en Postgres pero en SQLite hay decimales
    (p. ej. 2.5). Se redondea para que COPY no reviente."""
    if value is None or value == "":
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def main():
    apply = "--apply" in sys.argv

    con = sqlite3.connect(LOCAL_DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT " + ", ".join(COLUMNS) + " FROM news_items"
    ).fetchall()
    print(f"Local: {len(rows)} filas")

    dsn = neon_dsn()
    env = dict(os.environ, PGPASSWORD=dsn.split(":", 2)[2].split("@")[0])

    # URLs ya presentes en Neon
    out = subprocess.run(
        ["psql", dsn, "-tAc", "select url from news_items"],
        capture_output=True, text=True, env=env, check=True,
    )
    existing = {u.strip() for u in out.stdout.splitlines() if u.strip()}
    print(f"Neon: {len(existing)} URLs ya presentes")

    missing = [r for r in rows if (r["url"] or "").strip() not in existing]
    print(f"A importar: {len(missing)}")

    if not missing:
        print("Nada que hacer.")
        return

    # CSV para \\copy de psql: más robusto que INSERT gigantes para 495 filas.
    csv_path = "/tmp/news_import.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        for r in missing:
            w.writerow([
                to_uuid(r["id"]),
                clean(r["title"]),
                clean(r["url"]),
                clean(r["publishedAt"]) or None,
                clean(r["description"]),
                clean(r["imageUrl"]),
                rating(r["relevance_rating"]),
                norm_sectors(r["sectors"]),
                clean(r["sourceName"]),
                clean(r["sourceId"]),
                clean(r["created_at"]) or None,
                clean(r["updated_at"]) or None,
                "true" if r["is_community"] in (1, "1", True) else "false",
                clean(r["submitted_by_user_id"]),
            ])
    print(f"CSV escrito: {csv_path}")

    if not apply:
        print("\nDRY RUN. Revisa el CSV. Para insertar de verdad: --apply")
        return

    copy_sql = (
        "\\copy news_items (" + ", ".join(f'"{c}"' for c in COLUMNS) + ") "
        f"FROM '{csv_path}' WITH (FORMAT csv, NULL '')"
    )
    # ON CONFLICT DO NOTHING evita reventar si algo entra en paralelo.
    wrapped = (
        "BEGIN;\n"
        "CREATE TEMP TABLE tmp_news (LIKE news_items INCLUDING DEFAULTS) ON COMMIT DROP;\n"
        + copy_sql.replace('news_items (', 'tmp_news (', 1) + ";\n"
        "INSERT INTO news_items (" + ", ".join(f'"{c}"' for c in COLUMNS) + ") "
        "SELECT " + ", ".join(f'"{c}"' for c in COLUMNS) + " FROM tmp_news "
        "ON CONFLICT (id) DO NOTHING;\n"
        "COMMIT;\n"
    )
    sql_path = "/tmp/news_import.sql"
    with open(sql_path, "w") as fh:
        fh.write(wrapped)

    res = subprocess.run(
        ["psql", dsn, "-v", "ON_ERROR_STOP=1", "-f", sql_path],
        capture_output=True, text=True, env=env,
    )
    print(res.stdout[-800:])
    if res.returncode != 0:
        print("ERROR:", res.stderr[-800:])
        sys.exit(1)

    count = subprocess.run(
        ["psql", dsn, "-tAc", "select count(*) from news_items"],
        capture_output=True, text=True, env=env, check=True,
    ).stdout.strip()
    print(f"Total en Neon tras importar: {count}")


if __name__ == "__main__":
    main()
