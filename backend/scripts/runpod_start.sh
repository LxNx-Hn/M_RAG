#!/usr/bin/env bash
set -euo pipefail

# Cloud GPU startup helper (Alice Cloud / RunPod / 임의 Linux GPU 환경 공용).
# 스크립트 위치 기준 절대경로를 사용하므로 어떤 작업 디렉토리에서 실행해도 동작.
# 환경별 차이는 환경변수로만 흡수한다 — 하드코딩 경로 없음.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"        # = backend/
PROJECT_DIR="$(cd "${ROOT_DIR}/.." && pwd)"        # = repo root (M_RAG/)

cd "$ROOT_DIR"

# HuggingFace 캐시 — config.py 의 setdefault 와 일관. 외부에서 export 한 경우 그 값 유지.
HF_CACHE_DEFAULT="${PROJECT_DIR}/hf_cache"
mkdir -p "$HF_CACHE_DEFAULT"
export HF_HOME="${HF_HOME:-$HF_CACHE_DEFAULT}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-$HF_HOME}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-$HF_HOME}"

# 평가 실행 기본값
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./mrag.db}"
export GENERATION_MODEL="${GENERATION_MODEL:-K-intelligence/Midm-2.0-Base-Instruct}"
export LOAD_GPU_MODELS="${LOAD_GPU_MODELS:-true}"
export MRAG_API_BASE="${MRAG_API_BASE:-http://127.0.0.1:8000}"
export SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-true}"

# JWT_SECRET_KEY 미설정 시 ephemeral 키 생성 — 매 기동마다 발급된 토큰은 종료 시 무효화됨.
if [ -z "${JWT_SECRET_KEY:-}" ]; then
  if command -v python3 >/dev/null 2>&1; then
    export JWT_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
  else
    export JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
  fi
  echo "[start] generated ephemeral JWT_SECRET_KEY"
fi

echo "[start] HF_HOME=$HF_HOME"
echo "[start] GENERATION_MODEL=$GENERATION_MODEL"
echo "[start] starting uvicorn"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" || true
  fi
}
trap cleanup EXIT

python scripts/verify_deployment.py
echo "[start] module import checks passed"

# health 폴링 (sleep 10 단순 대기 대신 모델 로드 완료까지 대기)
echo "[start] waiting for /health to report ready..."
for i in $(seq 1 60); do
  if curl -fsS "$MRAG_API_BASE/health" >/dev/null 2>&1; then
    echo "[start] health check passed"
    break
  fi
  sleep 2
  if [ "$i" -eq 60 ]; then
    echo "[start] health endpoint did not become ready within 120s"
    exit 1
  fi
done

wait "$SERVER_PID"
