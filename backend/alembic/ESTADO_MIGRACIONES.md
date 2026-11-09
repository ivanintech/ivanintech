# Estado de las migraciones Alembic (2026-11-09)

## Resumen
La base de datos de producción (Neon) funciona correctamente. Las migraciones
**no se aplican** sobre la BD poblada: `scripts/prestart.sh` detecta que hay
tablas y las omite. Esto es deliberado.

## El problema
`alembic_version` en Neon contiene `0b245c714296`, una revisión que **no existe**
en `alembic/versions/`. Es decir, la BD se creó con un esquema de otra rama del
proyecto y el marcador quedó huérfano.

## Por qué NO se arregla marcando la head
La head real del repo es `0679ddf92335`, y lo que hace su `upgrade()` es:

```python
op.drop_index(op.f('ix_apscheduler_jobs_next_run_time'), table_name='apscheduler_jobs')
op.drop_table('apscheduler_jobs')
```

Es decir: **borra la tabla del scheduler**. Pero `app/main.py:56` usa
`SQLAlchemyJobStore(url=sync_db_url)` sobre esa misma tabla, y ahora mismo hay
**4 jobs programados** en ella.

Marcar la head con `alembic stamp 0679ddf92335` haría que el siguiente
`alembic upgrade head` borrase `apscheduler_jobs` y dejase el planificador de
noticias sin persistencia.

## Cadena de revisiones (una sola head)
```
a76de84ab972 (raíz, down=None)
  └─ 1816b573ea9a
      └─ 2a7a5a062378
          └─ 9f0346115888
              └─ 4e0475a8c061
                  └─ 90eb69a0f500
                      ├─ b2711c6722c6 ─ e9f574a02116 ─┐
                      └─ dfa5ec2e84d4 ─ 9f6654de1ec5 ─┴─ 9c3c759fa74d
                                                           └─ 0679ddf92335  ← HEAD
```
Las dos ramas convergen en `9c3c759fa74d`. No hay heads divergentes
(`alembic heads` devuelve solo `0679ddf92335`).

## Qué haría falta para sanearlo de verdad
1. Borrar el fichero `0679ddf92335` (o vaciar su `upgrade()`), porque eliminar
   `apscheduler_jobs` contradice el `main.py` actual.
2. Crear una revisión nueva que documente el esquema real de producción.
3. `alembic stamp <esa_nueva_revision>` sobre Neon.

Mientras tanto: **no ejecutar `alembic upgrade head` contra Neon**. Se perdería
la tabla del scheduler y sus 4 jobs.
