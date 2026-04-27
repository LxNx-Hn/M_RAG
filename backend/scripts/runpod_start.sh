#!/usr/bin/env bash
set -euo pipefail

# RunPod startup helper (A100 target, no-SSH workflow)
# Execute from RunPod Web Terminal.

ROOT_DIR="/workspace/M_RAG/backend"
if [ ! -d "$ROOT_DIR" ]; then
  echo "Expected repository at $ROOT_DIR"
  exit 1
fi

cd "$ROOT_DIR"

mkdir -p /workspace/hf_cache
export HF_HOME=/workspace/hf_cache
export TRANSFORMERS_CACHE=/workspace/hf_cache
export HF_HUB_CACHE=/workspace/hf_cache

export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./mrag.db}"
export JWT_SECRET_KEY="${JWT_SECRET_KEY:-mrag-runpod-local-secret-change-me}"
export GENERATION_MODEL="${GENERATION_MODEL:-K-intelligence/Midm-2.0-Base-Instruct}"
export LOAD_GPU_MODELS="${LOAD_GPU_MODELS:-true}"
export MRAG_API_BASE="${MRAG_API_BASE:-http://127.0.0.1:8000}"
export SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-true}"

echo "[runpod_start] starting uvicorn with model=$GENERATION_MODEL"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" || true
  fi
}
trap cleanup EXIT

python scripts/verify_deployment.py
echo "[runpod_start] module import checks passed"
sleep 10
curl -fsS "$MRAG_API_BASE/health" >/dev/null
echo "[runpod_start] health check passed"

wait "$SERVER_PID"
