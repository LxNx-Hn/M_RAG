#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_ROOT="$(cd "${BACKEND_DIR}/.." && pwd)"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"
API_BASE="${MRAG_API_BASE:-http://127.0.0.1:8000}"
RESULTS_DIR="${BACKEND_DIR}/evaluation/results"
SERVER_LOG="${BACKEND_DIR}/scripts/rerun_uvicorn_stdout.log"

if [[ ! -x "${VENV_PYTHON}" ]]; then
  echo "[rerun] missing venv python at ${VENV_PYTHON}" >&2
  exit 1
fi

cd "${BACKEND_DIR}"

bash "${SCRIPT_DIR}/backup_alice_run.sh"

status_lines="$(git -C "${REPO_ROOT}" status --porcelain || true)"
code_changes="$(printf '%s\n' "${status_lines}" | grep -v '^$' | grep -v 'backend/evaluation/results/' || true)"
if [[ -n "${code_changes}" ]]; then
  echo "[rerun] git working tree has non-result changes; aborting before pull" >&2
  printf '%s\n' "${code_changes}" >&2
  exit 1
fi

pkill -f "scripts/master_run.py" || true
pkill -f "uvicorn api.main:app" || true
sleep 3

git -C "${REPO_ROOT}" fetch origin
git -C "${REPO_ROOT}" pull --ff-only origin main

export JWT_SECRET_KEY="${JWT_SECRET_KEY:-mrag-experiment-local-secret-2026}"
export LOAD_GPU_MODELS="${LOAD_GPU_MODELS:-true}"
export GENERATION_MODEL="${GENERATION_MODEL:-K-intelligence/Midm-2.0-Base-Instruct}"
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./mrag.db}"

nohup "${VENV_PYTHON}" -m uvicorn api.main:app --host 0.0.0.0 --port 8000 > "${SERVER_LOG}" 2>&1 &
SERVER_PID=$!
echo "[rerun] started uvicorn pid=${SERVER_PID}"

for _ in {1..60}; do
  if curl -fsS "${API_BASE}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 5
done

if ! curl -fsS "${API_BASE}/health" >/dev/null 2>&1; then
  echo "[rerun] API server failed to become healthy" >&2
  exit 1
fi

export MRAG_API_TOKEN="$("${VENV_PYTHON}" - <<'PY'
from datetime import datetime, timedelta, timezone
import os
import uuid

from jose import jwt

secret = os.environ["JWT_SECRET_KEY"]
now = datetime.now(timezone.utc)
payload = {
    "sub": "master_runner_bypass",
    "email": "runner@mrag.local",
    "exp": now + timedelta(hours=24),
    "iat": now,
    "jti": str(uuid.uuid4()),
    "token_type": "access",
}
print(jwt.encode(payload, secret, algorithm="HS256"))
PY
)"

"${VENV_PYTHON}" evaluation/run_track1.py \
  --mode ablation \
  --queries evaluation/data/pseudo_gt_track1.json \
  --papers paper_nlp_bge paper_nlp_rag paper_nlp_cad paper_nlp_raptor 1810.04805_bert 2101.08577 paper_korean \
  --output evaluation/results/table1_track1.json \
  --api-base "${API_BASE}" \
  --resume \
  --config-names "Full System: + CAD + SCD + Compression"

"${VENV_PYTHON}" evaluation/run_track1.py \
  --mode decoder \
  --queries evaluation/data/pseudo_gt_track1.json \
  --papers paper_nlp_cad paper_korean \
  --output evaluation/results/table2_decoder.json \
  --api-base "${API_BASE}" \
  --resume \
  --config-names "CAD only (alpha=0.5)" "CAD+SCD (alpha=0.5, beta=0.3)"

"${VENV_PYTHON}" evaluation/run_track1.py \
  --mode alpha-sweep \
  --queries evaluation/data/pseudo_gt_track1.json \
  --papers paper_nlp_cad paper_nlp_bge \
  --output evaluation/results/table2_alpha.json \
  --api-base "${API_BASE}" \
  --resume

"${VENV_PYTHON}" evaluation/run_track1.py \
  --mode beta-sweep \
  --queries evaluation/data/pseudo_gt_track1.json \
  --papers paper_korean \
  --output evaluation/results/table2_beta.json \
  --api-base "${API_BASE}" \
  --resume

"${VENV_PYTHON}" evaluation/run_track2.py \
  --mode domain \
  --queries evaluation/data/pseudo_gt_track2.json \
  --papers paper_nlp_bge paper_nlp_rag paper_nlp_cad paper_nlp_raptor \
  --output evaluation/results/table3_domain.json \
  --api-base "${API_BASE}" \
  --timeout 240 \
  --max-retries 8 \
  --retry-backoff 3.0 \
  --resume

"${VENV_PYTHON}" scripts/results_to_markdown.py \
  --input "${RESULTS_DIR}" \
  --output evaluation/results/TABLES.md

echo "[rerun] CAD-affected rerun completed"
