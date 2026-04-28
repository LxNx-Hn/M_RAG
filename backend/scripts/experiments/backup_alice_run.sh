#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="${BACKEND_DIR}/artifacts/alice_backups/${STAMP}"

mkdir -p "${BACKUP_DIR}"

copy_if_exists() {
  local src="$1"
  local dest="$2"
  if [[ -e "${src}" ]]; then
    mkdir -p "$(dirname "${dest}")"
    cp -R "${src}" "${dest}"
  fi
}

copy_if_exists "${BACKEND_DIR}/scripts/master_run.log" "${BACKUP_DIR}/master_run.log"
copy_if_exists "${BACKEND_DIR}/scripts/master_run_stdout.log" "${BACKUP_DIR}/master_run_stdout.log"
copy_if_exists "${BACKEND_DIR}/evaluation/results" "${BACKUP_DIR}/results"

echo "[backup] saved Alice artifacts to ${BACKUP_DIR}"
