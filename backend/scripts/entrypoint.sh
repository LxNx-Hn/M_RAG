#!/usr/bin/env bash
set -euo pipefail

cd /app

if [ "${SKIP_MIGRATIONS:-false}" = "true" ]; then
  echo "[entrypoint] SKIP_MIGRATIONS=true -> skipping Alembic migrations"
else
  echo "[entrypoint] Running Alembic migrations..."
  alembic upgrade head
fi

echo "[entrypoint] Starting API server..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-1}"
