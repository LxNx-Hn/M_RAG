#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups/$TIMESTAMP}"
DATA_DIR="${MRAG_DATA_DIR:-$ROOT_DIR/data}"
CHROMA_DIR="${MRAG_CHROMA_DIR:-$ROOT_DIR/chroma_db}"
mkdir -p "$BACKUP_DIR"

echo "Backup directory: $BACKUP_DIR"

if [[ -n "${DATABASE_URL:-}" ]] && [[ "$DATABASE_URL" == postgresql* ]]; then
  echo "Creating PostgreSQL dump..."
  pg_dump "$DATABASE_URL" > "$BACKUP_DIR/postgres.sql"
else
  echo "Skipping PostgreSQL dump because DATABASE_URL is not set to PostgreSQL."
fi

archive_dir() {
  local source_dir="$1"
  local archive_name="$2"

  if [[ ! -d "$source_dir" ]]; then
    echo "Skipping $archive_name because directory does not exist: $source_dir"
    return
  fi

  local parent_dir
  local base_name
  parent_dir="$(cd "$(dirname "$source_dir")" && pwd)"
  base_name="$(basename "$source_dir")"
  tar -czf "$BACKUP_DIR/$archive_name" -C "$parent_dir" "$base_name"
}

echo "Archiving runtime vector store and uploaded data..."
archive_dir "$CHROMA_DIR" "chroma_db.tar.gz"
archive_dir "$DATA_DIR" "data.tar.gz"

echo "Backup completed: $BACKUP_DIR"
