"""
M-RAG FastAPI 백엔드
다중 사용자 동시 접속을 위한 프로덕션 API 서버

실행:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1
    (GPU 모델은 프로세스 간 공유 불가 → workers=1, 동시성은 async로 처리)

프론트엔드 분리 배포:
    - FastAPI 백엔드: :8000 (API 서버)
    - React/Next.js 프론트엔드: :3000 (정적 빌드 또는 SPA)
"""
import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 프로젝트 루트 path 추가
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from api.dependencies import modules
from api.schemas import HealthResponse
from api.routers import papers, chat, citations
from api.routers import auth as auth_router
from api.routers import history as history_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 시 모듈 초기화/정리"""
    # 시작
    load_gpu = os.environ.get("LOAD_GPU_MODELS", "false").lower() == "true"
    logger.info(f"Starting M-RAG API (GPU models: {load_gpu})")
    modules.initialize(load_gpu_models=load_gpu)

    # DB 초기화 (선택적 — SQLAlchemy 없으면 스킵)
    try:
        from api.database import init_db
        await init_db()
    except Exception as e:
        logger.warning(f"DB init skipped: {e}")

    yield
    # 종료
    logger.info("Shutting down M-RAG API")


app = FastAPI(
    title="M-RAG API",
    description="모듈러 RAG 논문 리뷰 에이전트 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
)

# CORS — 프론트엔드 분리 배포 시 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server
        "http://localhost:5173",   # Vite dev server
        "*",                       # 개발 중 전체 허용 (프로덕션에서 제한)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(citations.router)
app.include_router(auth_router.router)
app.include_router(history_router.router)

# data 디렉토리 정적 서빙 (PDF 다운로드 등)
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
app.mount("/static/data", StaticFiles(directory=str(data_dir)), name="data")


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    """헬스체크 + 시스템 상태"""
    import torch

    collections = modules.vector_store.list_collections() if modules.is_initialized else []
    return HealthResponse(
        status="ok",
        modules_loaded=modules.is_initialized,
        gpu_available=torch.cuda.is_available(),
        collections=collections,
    )


@app.get("/", tags=["system"])
async def root():
    return {
        "name": "M-RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# 프론트엔드 서빙 방법:
# - 개발: Vite dev server (localhost:5173) → proxy /api, /health → FastAPI (localhost:8000)
# - 프로덕션: Nginx에서 프론트엔드 정적 파일 서빙 + /api 리버스 프록시
# - Docker: frontend 컨테이너 (Nginx) + backend 컨테이너 (FastAPI)
