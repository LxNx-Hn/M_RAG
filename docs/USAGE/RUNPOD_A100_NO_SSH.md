# RunPod A100 무SSH 실험 가이드

- 문서 기준 2026-04-27
- 목적 GHCR 컨테이너를 RunPod에서 pull해서 논문 실험 실행
- 기준 설정 Base 모델 + SQLite + SQLAlchemy

## 0) 가장 빠른 방법 원샷 스크립트

```bash
cd /workspace/M_RAG
GHCR_OWNER_LC=<github-owner-lowercase> bash backend/scripts/runpod_one_shot.sh
```

- private 패키지면 아래 환경변수 추가 후 실행

```bash
GHCR_USERNAME=<github-username> \
GHCR_TOKEN=<pat_read_packages> \
GHCR_OWNER_LC=<github-owner-lowercase> \
bash backend/scripts/runpod_one_shot.sh
```

- 원샷 스크립트 수행 내용
  - `docker pull`
  - 기존 컨테이너 제거
  - 새 컨테이너 실행
  - `/health` 확인
  - `master_run.py --skip-server` 전체 실험 실행
  - 결과 `TABLES.md` 미리보기

## 1) GitHub에서 이미지 발행

- 워크플로 파일 `.github/workflows/publish-backend-image.yml`
- 트리거
  - `main` 또는 `master` push
  - 수동 실행 `workflow_dispatch`
- 발행 이미지
  - `ghcr.io/<github-owner-lowercase>/m-rag-backend:latest`
  - `ghcr.io/<github-owner-lowercase>/m-rag-backend:sha-<commit>`

확인 순서
1. GitHub Actions에서 `Publish Backend Image` 성공 확인
2. GitHub Packages에서 `m-rag-backend` 패키지 생성 확인
3. 패키지가 private이면 RunPod에서 GHCR 로그인 필요

## 2) 수동 절차가 필요할 때

### 2-1. 이미지 pull

public 패키지
```bash
docker pull ghcr.io/<github-owner-lowercase>/m-rag-backend:latest
```

private 패키지
```bash
echo "<github_pat_with_read_packages>" | docker login ghcr.io -u <github-username> --password-stdin
docker pull ghcr.io/<github-owner-lowercase>/m-rag-backend:latest
```

### 2-2. 컨테이너 실행

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

### 2-3. 상태 확인

```bash
curl -s http://127.0.0.1:8000/health
docker logs --tail 200 mrag-backend
```

### 2-4. 전체 실험 실행

```bash
docker exec mrag-backend \
  python scripts/master_run.py --skip-server
```

### 2-5. 결과 확인

```bash
ls /workspace/mrag_results
cat /workspace/mrag_results/TABLES.md
```

## 3) 실패 시 빠른 점검

- `401` 발생 시 `JWT_SECRET_KEY`가 컨테이너와 실행 명령에서 동일한지 확인
- GPU 미사용 시 `docker logs mrag-backend`에서 모델 로드 로그 확인
- 중단 후 재실행은 `run_track1.py`, `run_track2.py`의 `--resume` 사용
- SQLite 파일 경로는 컨테이너 내부 `./mrag.db` 기준

