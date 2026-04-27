# RunPod A100 무SSH 실험 가이드

- 문서 기준 2026-04-27
- 목적 GitHub Container Registry(GHCR)에 올린 백엔드 이미지를 RunPod에서 pull해서 논문 실험 실행
- 기준 설정 Base 모델 + SQLite + SQLAlchemy

## 1. GitHub에서 이미지 발행

- 워크플로 파일 `.github/workflows/publish-backend-image.yml`
- 트리거
  - `main` 또는 `master` push
  - 수동 실행 `workflow_dispatch`
- 발행 이미지
  - `ghcr.io/<github-owner-lowercase>/m-rag-backend:latest`
  - `ghcr.io/<github-owner-lowercase>/m-rag-backend:sha-<commit>`

### 확인 순서

1. GitHub Actions 탭에서 `Publish Backend Image` 성공 확인
2. GitHub Packages에서 `m-rag-backend` 패키지 생성 확인
3. 패키지가 private이면 RunPod에서 GHCR 로그인 필요

## 2. RunPod Web Terminal에서 pull

### 2-1. 패키지가 public일 때

```bash
docker pull ghcr.io/<github-owner-lowercase>/m-rag-backend:latest
```

### 2-2. 패키지가 private일 때

```bash
echo "<github_pat_with_read_packages>" | docker login ghcr.io -u <github-username> --password-stdin
docker pull ghcr.io/<github-owner-lowercase>/m-rag-backend:latest
```

## 3. 컨테이너 실행

```bash
docker run -d \
  --name mrag-backend \
  --gpus all \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./mrag.db" \
  -e JWT_SECRET_KEY="mrag-experiment-local-secret-2026" \
  -e GENERATION_MODEL="K-intelligence/Midm-2.0-Base-Instruct" \
  -e LOAD_GPU_MODELS="true" \
  -e SKIP_MIGRATIONS="true" \
  -v /workspace/mrag_data:/app/data \
  -v /workspace/mrag_chroma:/app/chroma_db \
  -v /workspace/mrag_results:/app/evaluation/results \
  -v /workspace/hf_cache:/home/appuser/.cache/huggingface \
  ghcr.io/<github-owner-lowercase>/m-rag-backend:latest
```

### 상태 확인

```bash
curl -s http://127.0.0.1:8000/health
docker logs --tail 200 mrag-backend
```

## 4. 실험 토큰 생성

```bash
python - <<'PY'
from jose import jwt
from datetime import datetime, timedelta, timezone
import uuid

secret = "mrag-experiment-local-secret-2026"
payload = {
    "sub": "runpod_eval_user",
    "email": "runpod@local",
    "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    "iat": datetime.now(timezone.utc),
    "jti": str(uuid.uuid4()),
    "token_type": "access",
}
print(jwt.encode(payload, secret, algorithm="HS256"))
PY
```

```bash
export MRAG_API_TOKEN="<paste_token>"
```

## 5. 논문 인덱싱

```bash
docker exec -e MRAG_API_TOKEN="$MRAG_API_TOKEN" mrag-backend \
  python scripts/index_papers.py --api-url http://127.0.0.1:8000
```

## 6. 전체 실험 실행

```bash
docker exec -e MRAG_API_TOKEN="$MRAG_API_TOKEN" mrag-backend \
  python scripts/master_run.py --skip-download --skip-server
```

## 7. 결과 확인

```bash
ls /workspace/mrag_results
cat /workspace/mrag_results/TABLES.md
```

## 8. 실패 시 빠른 점검

- `401` 발생 시 `MRAG_API_TOKEN` 재발급 후 다시 실행
- GPU 미사용 시 `docker logs mrag-backend`에서 모델 로드 로그 확인
- 중단 후 재실행은 `run_track1.py`, `run_track2.py`의 `--resume` 사용
- SQLite 파일 경로는 컨테이너 내부 `./mrag.db` 기준

