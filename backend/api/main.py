"""
M-RAG FastAPI backend entrypoint.
"""

import json
import logging
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from api.auth import SECRET_KEY  # noqa: F401  # Fail fast when unset
from api.database import get_engine, init_db
from api.dependencies import modules
from api.limiter import limiter
from api.routers import auth as auth_router
from api.routers import chat, citations, history as history_router, papers
from api.schemas import HealthResponse


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            payload["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            payload["user_id"] = record.user_id
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> logging.Logger:
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "mrag.log"

    formatter = JsonFormatter()
    stream_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    return logging.getLogger(__name__)


logger = configure_logging()


def parse_cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ALLOW_ORIGINS", "").strip()
    if not raw:
        return ["http://localhost:3000", "http://localhost:5173"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def parse_cors_credentials(origins: list[str]) -> bool:
    allow_credentials = (
        os.environ.get("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
    )
    if "*" in origins and allow_credentials:
        logger.warning(
            "CORS credentials disabled because wildcard origins are configured"
        )
        return False
    return allow_credentials


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_gpu = os.environ.get("LOAD_GPU_MODELS", "false").lower() == "true"
    logger.info(json.dumps({"event": "startup", "gpu_models": load_gpu}))
    modules.initialize(load_gpu_models=load_gpu)
    await init_db()
    if modules.is_initialized and modules.vector_store and modules.hybrid_retriever:
        for collection_name in modules.vector_store.list_collections():
            try:
                modules.hybrid_retriever.fit_bm25(collection_name)
            except Exception as exc:
                logger.warning("BM25 rebuild failed for %s: %s", collection_name, exc)
    yield
    logger.info(json.dumps({"event": "shutdown"}))


app = FastAPI(
    title="M-RAG API",
    description="Modular RAG paper review agent API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

cors_origins = parse_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=parse_cors_credentials(cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(citations.router)
app.include_router(auth_router.router)
app.include_router(history_router.router)

data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
app.mount("/static/data", StaticFiles(directory=str(data_dir)), name="data")


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "request_failed",
            extra={"request_id": request_id},
        )
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    user_id = getattr(request.state, "user_id", "")
    logger.info(
        json.dumps(
            {
                "event": "request",
                "request_id": request_id,
                "user_id": user_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
            ensure_ascii=False,
        ),
        extra={"request_id": request_id, "user_id": user_id},
    )
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    csp = os.environ.get(
        "SECURITY_CSP",
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'",
    )
    response.headers["Content-Security-Policy"] = csp
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if os.environ.get("ENV", "development").lower() == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        json.dumps(
            {
                "event": "http_error",
                "path": request.url.path,
                "status_code": exc.status_code,
                "detail": exc.detail,
            },
            ensure_ascii=False,
        ),
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", None),
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        json.dumps(
            {
                "event": "validation_error",
                "path": request.url.path,
                "errors": exc.errors(),
            },
            ensure_ascii=False,
        ),
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", None),
        },
    )
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled error",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", None),
        },
    )
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": "Unexpected server error"},
    )


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    import torch
    from sqlalchemy import text

    collections = []
    chroma_connected = False
    database_connected = False

    if modules.is_initialized and modules.vector_store is not None:
        try:
            collections = modules.vector_store.list_collections()
            chroma_connected = True
        except Exception:
            chroma_connected = False

    engine = get_engine()
    if engine is not None:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            database_connected = True
        except Exception:
            database_connected = False

    return HealthResponse(
        status="ok" if chroma_connected and database_connected else "degraded",
        modules_loaded=modules.is_initialized,
        gpu_available=torch.cuda.is_available(),
        collections=collections,
        database_connected=database_connected,
        chroma_connected=chroma_connected,
        generator_loaded=modules.has_generator,
        embedder_loaded=modules.embedder is not None,
    )


@app.get("/", tags=["system"])
async def root():
    return {
        "name": "M-RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
