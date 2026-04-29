#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_ROOT="$(cd "${BACKEND_DIR}/.." && pwd)"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"
API_BASE="${MRAG_API_BASE:-http://127.0.0.1:8000}"
COLLECTION_NAME="${MRAG_COLLECTION_NAME:-papers}"
RESULTS_DIR="${BACKEND_DIR}/evaluation/results"
SERVER_LOG="${BACKEND_DIR}/scripts/rerun_uvicorn_stdout.log"
RERUN_LOG="${BACKEND_DIR}/scripts/rerun_cad_affected_stdout.log"

if [[ ! -x "${VENV_PYTHON}" ]]; then
  echo "[rerun] missing venv python at ${VENV_PYTHON}" >&2
  exit 1
fi

cd "${BACKEND_DIR}"

set +u
for env_file in \
  "$HOME/.bashrc" \
  "$HOME/.profile" \
  "${REPO_ROOT}/.env" \
  "${BACKEND_DIR}/.env"
do
  if [[ -f "${env_file}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${env_file}"
    set +a
  fi
done
set -u

status_lines="$(git -C "${REPO_ROOT}" status --porcelain || true)"
code_changes="$(printf '%s\n' "${status_lines}" | grep -v '^$' | grep -v 'backend/evaluation/results/' | grep -v 'backend/artifacts/' || true)"
if [[ -n "${code_changes}" ]]; then
  echo "[rerun] git working tree has non-result changes; aborting before pull" >&2
  printf '%s\n' "${code_changes}" >&2
  exit 1
fi

bash "${SCRIPT_DIR}/backup_alice_run.sh"

pkill -f "scripts/master_run.py" || true
pkill -f "scripts/generate_pseudo_gt.py" || true
pkill -f "evaluation/run_track1.py" || true
pkill -f "evaluation/run_track2.py" || true
pkill -f "uvicorn api.main:app" || true
sleep 3

git -C "${REPO_ROOT}" fetch origin
git -C "${REPO_ROOT}" pull --ff-only origin main

export JWT_SECRET_KEY="${JWT_SECRET_KEY:-mrag-experiment-local-secret-2026}"
export LOAD_GPU_MODELS="${LOAD_GPU_MODELS:-true}"
export GENERATION_MODEL="${GENERATION_MODEL:-K-intelligence/Midm-2.0-Base-Instruct}"
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./mrag.db}"
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-$HF_HOME}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-$HF_HOME}"
export OPENAI_JUDGE_MODEL="${OPENAI_JUDGE_MODEL:-gpt-4o}"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "[rerun] OPENAI_API_KEY is required for clean STEP 5 rerun." >&2
  exit 1
fi

mkdir -p "${RESULTS_DIR}"

# Archive existing result files instead of deleting
ARCHIVE_TS="$(date +%Y%m%d_%H%M%S)"
ARCHIVE_DIR="${RESULTS_DIR}/_archive/${ARCHIVE_TS}"
ARCHIVE_FILES="$(find "${RESULTS_DIR}" -maxdepth 1 -type f \( -name "*.json" -o -name "TABLES.md" \) 2>/dev/null)"
if [[ -n "${ARCHIVE_FILES}" ]]; then
  mkdir -p "${ARCHIVE_DIR}"
  echo "${ARCHIVE_FILES}" | xargs -I{} mv {} "${ARCHIVE_DIR}/"
  echo "[rerun] archived previous results to ${ARCHIVE_DIR}"
fi

rm -f "${BACKEND_DIR}/evaluation/data/pseudo_gt_track1.json"
rm -f "${BACKEND_DIR}/evaluation/data/pseudo_gt_track2.json"
rm -f "${BACKEND_DIR}/scripts/master_run.log"
rm -f "${BACKEND_DIR}/logs/manual_uvicorn.err"
rm -f "${BACKEND_DIR}/logs/manual_uvicorn.out"
find "${BACKEND_DIR}/logs" -maxdepth 1 -type f -name "run_all_experiments_*.err" -delete
find "${BACKEND_DIR}/logs" -maxdepth 1 -type f -name "run_all_experiments_*.out" -delete
: > "${BACKEND_DIR}/logs/mrag.log"
: > "${SERVER_LOG}"
: > "${RERUN_LOG}"

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

# Bootstrap runner account: register, then login if already exists
RUNNER_EMAIL="${MRAG_RUNNER_EMAIL:-runner@mrag.local}"
RUNNER_USERNAME="${MRAG_RUNNER_USERNAME:-master_runner}"
RUNNER_PASSWORD="${MRAG_RUNNER_PASSWORD:-MragRunner!2026x}"

REGISTER_RESP="$(curl -s -w '\n%{http_code}' -X POST "${API_BASE}/api/auth/register" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${RUNNER_EMAIL}\",\"username\":\"${RUNNER_USERNAME}\",\"password\":\"${RUNNER_PASSWORD}\"}")"
REGISTER_HTTP="$(echo "${REGISTER_RESP}" | tail -n1)"
REGISTER_BODY="$(echo "${REGISTER_RESP}" | sed '$d')"

if [[ "${REGISTER_HTTP}" == "200" ]] || [[ "${REGISTER_HTTP}" == "201" ]]; then
  export MRAG_API_TOKEN="$(echo "${REGISTER_BODY}" | "${VENV_PYTHON}" -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')"
  echo "[rerun] runner account registered, token acquired"
elif [[ "${REGISTER_HTTP}" == "409" ]]; then
  echo "[rerun] runner account exists, logging in"
  LOGIN_RESP="$(curl -s -w '\n%{http_code}' -X POST "${API_BASE}/api/auth/login" \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"${RUNNER_EMAIL}\",\"password\":\"${RUNNER_PASSWORD}\"}")"
  LOGIN_HTTP="$(echo "${LOGIN_RESP}" | tail -n1)"
  LOGIN_BODY="$(echo "${LOGIN_RESP}" | sed '$d')"
  if [[ "${LOGIN_HTTP}" != "200" ]]; then
    echo "[rerun] login failed (HTTP ${LOGIN_HTTP}): ${LOGIN_BODY}" >&2
    exit 1
  fi
  export MRAG_API_TOKEN="$(echo "${LOGIN_BODY}" | "${VENV_PYTHON}" -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')"
  echo "[rerun] login successful, token acquired"
else
  echo "[rerun] register failed (HTTP ${REGISTER_HTTP}): ${REGISTER_BODY}" >&2
  exit 1
fi

"${VENV_PYTHON}" scripts/generate_pseudo_gt.py \
  --collection "${COLLECTION_NAME}" \
  --api-url "${API_BASE}" \
  --input evaluation/data/track1_queries.json \
  --output evaluation/data/pseudo_gt_track1.json \
  --timeout 180 \
  --max-retries 8 \
  --retry-backoff 2.0 \
  --min-interval 1.0 \
  --gt-model gpt-4o \
  --search-top-k 10 \
  --force

"${VENV_PYTHON}" scripts/generate_pseudo_gt.py \
  --collection "${COLLECTION_NAME}" \
  --api-url "${API_BASE}" \
  --input evaluation/data/track2_queries.json \
  --output evaluation/data/pseudo_gt_track2.json \
  --timeout 180 \
  --max-retries 8 \
  --retry-backoff 2.0 \
  --min-interval 1.0 \
  --gt-model gpt-4o \
  --search-top-k 10 \
  --force

"${VENV_PYTHON}" evaluation/run_track1.py \
  --mode ablation \
  --queries evaluation/data/pseudo_gt_track1.json \
  --papers paper_nlp_bge paper_nlp_rag paper_nlp_cad paper_nlp_raptor paper_midm paper_ko_rag_eval_framework paper_ko_hyde_multihop paper_ko_cad_contrastive \
  --output evaluation/results/table1_track1.json \
  --api-base "${API_BASE}" \
  --judge-model "${OPENAI_JUDGE_MODEL}"

"${VENV_PYTHON}" evaluation/run_track1.py \
  --mode decoder \
  --queries evaluation/data/pseudo_gt_track1.json \
  --papers paper_nlp_cad paper_ko_cad_contrastive \
  --output evaluation/results/table2_decoder.json \
  --api-base "${API_BASE}" \
  --judge-model "${OPENAI_JUDGE_MODEL}"

"${VENV_PYTHON}" evaluation/run_track1.py \
  --mode alpha-sweep \
  --queries evaluation/data/pseudo_gt_track1.json \
  --papers paper_nlp_cad paper_nlp_bge \
  --output evaluation/results/table2_alpha.json \
  --api-base "${API_BASE}" \
  --judge-model "${OPENAI_JUDGE_MODEL}"

"${VENV_PYTHON}" evaluation/run_track1.py \
  --mode beta-sweep \
  --queries evaluation/data/pseudo_gt_track1.json \
  --papers paper_ko_hyde_multihop \
  --output evaluation/results/table2_beta.json \
  --api-base "${API_BASE}" \
  --judge-model "${OPENAI_JUDGE_MODEL}"

"${VENV_PYTHON}" evaluation/run_track2.py \
  --mode domain \
  --queries evaluation/data/pseudo_gt_track2.json \
  --papers paper_nlp_bge paper_nlp_rag paper_nlp_cad paper_nlp_raptor paper_midm paper_ko_rag_eval_framework paper_ko_hyde_multihop paper_ko_cad_contrastive \
  --output evaluation/results/table3_domain.json \
  --api-base "${API_BASE}" \
  --timeout 240 \
  --max-retries 8 \
  --retry-backoff 3.0 \
  --judge-model "${OPENAI_JUDGE_MODEL}"

"${VENV_PYTHON}" scripts/results_to_markdown.py \
  --input "${RESULTS_DIR}" \
  --output evaluation/results/TABLES.md

echo "[rerun] CAD-affected rerun completed"
