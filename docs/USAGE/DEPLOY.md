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
npm run dev -- --host 0.0.0.0
```

## Docker Compose

```powershell
docker compose up --build
```

운영 DB를 쓰려면 `.env`에 PostgreSQL 값을 설정한다.

## 결과 위치

- JSON 결과 `experiments/results/*.json`
- Markdown 표 `experiments/results/TABLES.md`
- 실행 로그 `experiments/reports/` 또는 실행별 지정 로그
- 실험 소스 PDF `experiments/data/source_papers/`
- 런타임 업로드 PDF `MRAG_DATA_DIR` 또는 마운트된 runtime data 볼륨
- ChromaDB `MRAG_CHROMA_DIR` 또는 마운트된 runtime vector-store 볼륨

## 배포 검증

```powershell
python -m compileall backend experiments
python experiments\runners\dry_run_matrix.py --experiment main-hyde-cad-scd --estimate-cost --dry-run
```

