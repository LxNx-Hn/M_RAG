#!/usr/bin/env bash
set -euo pipefail

cd /app

echo "[entrypoint] Running Alembic migrations..."
alembic upgrade head

echo "[entrypoint] Starting API server..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-1}"
