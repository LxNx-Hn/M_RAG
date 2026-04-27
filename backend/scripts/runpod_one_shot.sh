#!/usr/bin/env bash
set -euo pipefail

# One-shot runner for RunPod Web Terminal:
# pull image -> run container -> wait health -> run full thesis experiment.
#
# Usage examples:
#   GHCR_OWNER_LC=lxnx-hn bash backend/scripts/runpod_one_shot.sh
#   GHCR_IMAGE=ghcr.io/lxnx-hn/m-rag-backend:latest bash backend/scripts/runpod_one_shot.sh
#
# Optional private package auth:
#   GHCR_USERNAME=<user> GHCR_TOKEN=<pat_with_read:packages> ...

CONTAINER_NAME="${CONTAINER_NAME:-mrag-backend}"
API_PORT="${API_PORT:-8000}"

GHCR_OWNER_LC="${GHCR_OWNER_LC:-}"
GHCR_IMAGE="${GHCR_IMAGE:-}"
if [ -z "$GHCR_IMAGE" ]; then
  if [ -z "$GHCR_OWNER_LC" ]; then
    echo "Set GHCR_IMAGE or GHCR_OWNER_LC first."
    echo "Example: GHCR_OWNER_LC=lxnx-hn bash backend/scripts/runpod_one_shot.sh"
    exit 1
  fi
  GHCR_IMAGE="ghcr.io/${GHCR_OWNER_LC}/m-rag-backend:latest"
fi

DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./mrag.db}"
JWT_SECRET_KEY="${JWT_SECRET_KEY:-mrag-experiment-local-secret-2026}"
GENERATION_MODEL="${GENERATION_MODEL:-K-intelligence/Midm-2.0-Base-Instruct}"
LOAD_GPU_MODELS="${LOAD_GPU_MODELS:-true}"
SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-true}"

mkdir -p /workspace/mrag_data /workspace/mrag_chroma /workspace/mrag_results /workspace/hf_cache

if [ -n "${GHCR_USERNAME:-}" ] && [ -n "${GHCR_TOKEN:-}" ]; then
  echo "[one-shot] logging in to ghcr.io as ${GHCR_USERNAME}"
  echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USERNAME}" --password-stdin
fi

echo "[one-shot] pulling image: ${GHCR_IMAGE}"
docker pull "${GHCR_IMAGE}"

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "[one-shot] removing existing container: ${CONTAINER_NAME}"
  docker rm -f "${CONTAINER_NAME}" >/dev/null
fi

echo "[one-shot] starting container: ${CONTAINER_NAME}"
docker run -d \
  --name "${CONTAINER_NAME}" \
  --gpus all \
  -p "${API_PORT}:8000" \
  -e DATABASE_URL="${DATABASE_URL}" \
  -e JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
  -e GENERATION_MODEL="${GENERATION_MODEL}" \
  -e LOAD_GPU_MODELS="${LOAD_GPU_MODELS}" \
  -e SKIP_MIGRATIONS="${SKIP_MIGRATIONS}" \
  -v /workspace/mrag_data:/app/data \
  -v /workspace/mrag_chroma:/app/chroma_db \
  -v /workspace/mrag_results:/app/evaluation/results \
  -v /workspace/hf_cache:/home/appuser/.cache/huggingface \
  "${GHCR_IMAGE}" >/dev/null

echo "[one-shot] waiting for health endpoint"
for i in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${API_PORT}/health" >/dev/null 2>&1; then
    echo "[one-shot] health check passed"
    break
  fi
  if [ "$i" -eq 120 ]; then
    echo "[one-shot] health check timeout"
    docker logs --tail 200 "${CONTAINER_NAME}" || true
    exit 1
  fi
  sleep 2
done

echo "[one-shot] running full experiment via master_run.py"
docker exec "${CONTAINER_NAME}" \
  python scripts/master_run.py \
  --skip-server \
  --database-url "${DATABASE_URL}" \
  --jwt-secret "${JWT_SECRET_KEY}" \
  --generation-model "${GENERATION_MODEL}"

echo "[one-shot] completed. results:"
ls -lah /workspace/mrag_results || true
echo "[one-shot] preview:"
if [ -f /workspace/mrag_results/TABLES.md ]; then
  sed -n '1,80p' /workspace/mrag_results/TABLES.md
else
  echo "TABLES.md not found"
fi

