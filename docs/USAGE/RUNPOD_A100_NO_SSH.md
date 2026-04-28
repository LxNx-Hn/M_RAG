# RunPod A100 No-SSH 실험 가이드

## 목적

RunPod 웹 터미널만 사용해 논문 실험을 실행한다.

## 권장 사양

- A100 40GB 이상
- Storage 256GB 이상 권장
- CUDA 포함 이미지

## Git clone 방식

```bash
cd /workspace
git clone https://github.com/LxNx-Hn/M_RAG.git
cd M_RAG
python -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend/requirements.txt
```

모델과 데이터 준비

```bash
cd /workspace/M_RAG/backend
python scripts/download_models.py --llm-model K-intelligence/Midm-2.0-Base-Instruct
python scripts/download_test_papers.py
```

실험 실행

```bash
cd /workspace/M_RAG/backend
source ../.venv/bin/activate
export JWT_SECRET_KEY=mrag-experiment-local-secret-2026
export LOAD_GPU_MODELS=true
export GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct
nohup python scripts/master_run.py --skip-download > scripts/master_run_stdout.log 2>&1 &
```

진행 확인

```bash
tail -f /workspace/M_RAG/backend/scripts/master_run.log
```

결과 확인

```bash
cat /workspace/M_RAG/backend/evaluation/results/TABLES.md
```

## GHCR 컨테이너 방식

GitHub Packages에 backend image가 발행되어 있을 때만 사용한다.

```bash
docker pull ghcr.io/lxnx-hn/m-rag-backend:latest
docker run -d \
  --name mrag-backend \
  --gpus all \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./mrag.db" \
  -e JWT_SECRET_KEY="mrag-experiment-local-secret-2026" \
  -e GENERATION_MODEL="K-intelligence/Midm-2.0-Base-Instruct" \
  -e LOAD_GPU_MODELS="true" \
  -e SKIP_MIGRATIONS="true" \
  ghcr.io/lxnx-hn/m-rag-backend:latest
```

컨테이너 안에서 실험 실행

```bash
docker exec mrag-backend python scripts/master_run.py --skip-server
```

## 주의

- Docker가 없는 환경에서는 GHCR 컨테이너 방식이 동작하지 않는다
- 그런 경우 git clone + venv 방식을 사용한다
- 논문 실험은 SQLite로 충분하다
- PostgreSQL은 서비스/운영 시연 때 사용한다
