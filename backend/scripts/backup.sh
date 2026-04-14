#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups/$TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

echo "Backup directory: $BACKUP_DIR"

if [[ -n "${DATABASE_URL:-}" ]] && [[ "$DATABASE_URL" == postgresql* ]]; then
  echo "Creating PostgreSQL dump..."
  pg_dump "$DATABASE_URL" > "$BACKUP_DIR/postgres.sql"
else
  echo "Skipping PostgreSQL dump because DATABASE_URL is not set to PostgreSQL."
fi

echo "Archiving vector store and uploaded data..."
tar -czf "$BACKUP_DIR/chroma_db.tar.gz" -C "$ROOT_DIR" chroma_db
tar -czf "$BACKUP_DIR/data.tar.gz" -C "$ROOT_DIR" data

echo "Backup completed: $BACKUP_DIR"
