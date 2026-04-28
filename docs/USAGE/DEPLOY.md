# M-RAG 실행 및 배포 가이드

## 기준

- 논문 실험 기본 모델은 `K-intelligence/Midm-2.0-Base-Instruct`
- 로컬 스모크 검증은 `K-intelligence/Midm-2.0-Mini-Instruct` 선택 가능
- 논문 실험 빠른 실행은 SQLite + SQLAlchemy 사용
- 운영/서비스 경로는 PostgreSQL + SQLAlchemy 사용
- 논문 실험 경로는 MIDM Base 직접 디코딩을 기준으로 함

## 로컬 환경 준비

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend\requirements.txt
cd frontend
npm ci
cd ..
```

## 모델 캐시

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
python scripts\download_models.py --llm-model K-intelligence/Midm-2.0-Base-Instruct
```

Mini 스모크 검증

```powershell
python scripts\download_models.py --llm-model K-intelligence/Midm-2.0-Mini-Instruct
```

## 개발 서버 실행

Backend

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
$env:JWT_SECRET_KEY = "change-this-secret"
$env:LOAD_GPU_MODELS = "true"
$env:GENERATION_MODEL = "K-intelligence/Midm-2.0-Base-Instruct"
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Frontend

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\frontend
npm run dev
```

## 논문 실험 실행

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
$env:JWT_SECRET_KEY = "mrag-experiment-local-secret-2026"
$env:LOAD_GPU_MODELS = "true"
python scripts\master_run.py --skip-download
```

`master_run.py` 기본값

- `DATABASE_URL=sqlite+aiosqlite:///./mrag.db`
- `GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct`
- `LOAD_GPU_MODELS=true`

성공 기준

- `STEP 12 - Validate results completed successfully.`
- `STEP 13 - Stop the API server subprocess cleanly completed successfully.`
- `MASTER RUN COMPLETE`

## Docker Compose

```powershell
docker compose up --build
```

운영 DB를 쓰려면 `.env`에 PostgreSQL 값을 설정한다.

## 결과 위치

- JSON 결과 `backend/evaluation/results/*.json`
- Markdown 표 `backend/evaluation/results/TABLES.md`
- 실행 로그 `backend/scripts/master_run.log`
- 업로드/실험 PDF `backend/data/`
- ChromaDB `backend/chroma_db/`
