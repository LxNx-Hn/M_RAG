# M-RAG 최신 작업 계획

- 문서 기준 2026-04-28
- 목적 Alice Cloud GPU 에서 논문 실험을 완주하고 결과를 git pull 로 수신

## 목표

- `backend/scripts/master_run.py` 기준으로 전체 실험을 한 번에 실행
- `backend/evaluation/results/TABLES.md` 를 최신 결과로 재생성
- CAD + SCD 포함 생성 제어를 그대로 유지 (논문 클레임 기준)

## 이번 범위에서 하지 않는 것

- plain generation 전환
- 외부 상용 LLM API 연동
- `vLLM` 전환
- 이유 CAD와 SCD 기반 환각 억제와 언어 이탈 억제가 현재 논문 핵심 클레임

## Alice Cloud 실험 실행 계획

전체 절차는 `docs/USAGE/ALICE_CLOUD_GUIDE.md` 참조.

### 1 시작 전 점검

- `.env` 에 `OPENAI_API_KEY` 설정 여부 확인
- `backend/data/` PDF 파일 존재 여부 확인
- `nvidia-smi` 로 GPU VRAM 여유 확인

### 2 시작 명령

```bash
cd /home/elicer/M_RAG/backend
source ../.venv/bin/activate
nohup python scripts/master_run.py --skip-download \
  > scripts/master_run_stdout.log 2>&1 &
tail -f scripts/master_run.log
```

### 3 모니터링 포인트

- `generator_loaded` 확인 (STEP 3 모델 로드)
- `gpu_available` 확인
- STEP 6–10 각 config/paper 완료 로그 확인
- `Skipping completed` 메시지로 resume 동작 확인

### 4 완료 판정

- `STEP 12 - Validate results completed successfully.`
- `STEP 13 - Stop the API server subprocess cleanly completed successfully.`
- `MASTER RUN COMPLETE`
- `backend/evaluation/results/` 아래 결과 JSON 5종 + `TABLES.md` 생성
- 결과 값이 전부 동일 점수나 0 점수로 수렴하지 않는지 확인

## 운영 기준

- 기본 생성 모델 Base (`K-intelligence/Midm-2.0-Base-Instruct`)
- Mini 모델은 로컬 스모크 검증에서만
- DB Alice Cloud: SQLite, 운영 배포: PostgreSQL

## 실패 시 우선 확인

- stale `uvicorn api.main:app` 프로세스 (`pkill -f "uvicorn api.main:app"`)
- `OPENAI_API_KEY` 설정 여부 (`backend/.env`)
- CUDA 인식 (`nvidia-smi`)
- `backend/data/*.pdf` 존재 여부
- `backend/scripts/master_run.log` 마지막 성공 단계
- 중단 후 재실행: `master_run.py --skip-download` 그대로 재실행 (resume 자동)

## 결과 수신 (로컬 PC)

```bash
git pull origin main
ls backend/evaluation/results/
cat backend/evaluation/results/TABLES.md
```
