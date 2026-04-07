#!/bin/bash
# M-RAG 로컬 개발 실행 스크립트
# 사용법:
#   ./dev.sh          → 백엔드(FastAPI) + 프론트엔드(React) 동시 실행
#   ./dev.sh backend  → FastAPI만 실행
#   ./dev.sh frontend → React만 실행
#   ./dev.sh streamlit → Streamlit 프로토타입 실행
#   ./dev.sh docker   → Docker Compose로 전체 실행 (PostgreSQL 포함)

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# ─────────────────────────────────
# 색상 출력
# ─────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[M-RAG]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# ─────────────────────────────────
# 모드 선택
# ─────────────────────────────────
MODE="${1:-all}"

case "$MODE" in
  "backend")
    log "FastAPI 백엔드 실행 중... (http://localhost:8000)"
    info "Swagger UI: http://localhost:8000/docs"
    cd "$BACKEND_DIR"
    TOKENIZERS_PARALLELISM=false \
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    ;;

  "frontend")
    log "React 프론트엔드 실행 중... (http://localhost:5173)"
    cd "$FRONTEND_DIR"
    npm run dev
    ;;

  "streamlit")
    log "Streamlit 프로토타입 실행 중... (http://localhost:8501)"
    cd "$BACKEND_DIR"
    TOKENIZERS_PARALLELISM=false \
    streamlit run app.py
    ;;

  "docker")
    log "Docker Compose 실행 중..."
    info "서비스: db(PostgreSQL:5432) + backend(FastAPI:8000) + frontend(Nginx:3000)"
    if [ "${LOAD_GPU_MODELS}" = "true" ]; then
      info "GPU 모드 활성화 (LOAD_GPU_MODELS=true)"
    else
      warn "CPU 모드 (검색/재랭킹만 동작, LLM 비활성). GPU 활성화: LOAD_GPU_MODELS=true ./dev.sh docker"
    fi
    cd "$ROOT_DIR"
    docker compose up --build
    ;;

  "all"|*)
    log "백엔드 + 프론트엔드 동시 실행"
    info "백엔드: http://localhost:8000 (Swagger: http://localhost:8000/docs)"
    info "프론트엔드: http://localhost:5173"
    warn "PostgreSQL이 별도로 필요합니다. DB 없이 테스트하려면 ./dev.sh streamlit"

    # 종료 시 두 프로세스 모두 kill
    trap 'kill 0' EXIT

    # 백엔드 (백그라운드)
    (
      cd "$BACKEND_DIR"
      TOKENIZERS_PARALLELISM=false \
      uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    ) &

    # 프론트엔드 (포그라운드)
    (
      cd "$FRONTEND_DIR"
      npm run dev
    ) &

    wait
    ;;
esac
