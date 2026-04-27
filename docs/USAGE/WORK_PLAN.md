# M-RAG 최신 작업 계획

- 문서 기준 2026-04-27
- 목적 내일 바로 로컬 실험을 시작할 수 있게 실행 경로와 확인 기준을 고정

## 목표

- `backend/scripts/master_run.py` 기준으로 전체 실험을 한 번에 실행
- `backend/evaluation/results/TABLES.md` 를 최신 결과로 재생성
- 현재 논문 경로 기준인 CAD + SCD 포함 생성 제어를 그대로 유지

## 이번 구현에서 하지 않는 것

- plain generation 전환
- 외부 상용 LLM API 연동
- `vLLM` 전환
- 이유 현재 논문 클레임이 CAD와 SCD 기반 환각 억제와 언어 이탈 억제에 있기 때문
- OpenAI 같은 외부 API는 연결은 쉽지만 생성 중간 제어 유지에 불리
- `vLLM` 은 추론 효율 장점은 있지만 CAD와 SCD 특히 CAD를 유지하려면 별도 연구와 재구현이 필요

## 내일 실험 시작 계획

### 1 시작 전 점검

- PowerShell 새 창 열기
- `.venv` 활성화
- Python 중복 프로세스 확인
- `:8000` 포트 점유 여부 확인
- GPU 메모리 상태 확인
- `backend/data/` 와 `backend/evaluation/data/` 입력 파일 존재 확인

### 2 시작 명령

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
.venv\Scripts\Activate.ps1
cd backend
python scripts\master_run.py --skip-download
```

### 3 실행 중 모니터링

```powershell
Get-Content C:\Users\KiKi\Desktop\CODE\M_RAG\backend\scripts\master_run.log -Wait -Tail 40
```

- `generator_loaded` 확인
- `gpu_available` 확인
- 인덱싱 이후 Track 1 과 Track 2 단계가 실제로 이어지는지 확인
- 중복 서버나 stale `uvicorn` 징후가 없는지 확인

### 4 완료 판정

- `STEP 12 - Validate results completed successfully.`
- `STEP 13 - Stop the API server subprocess cleanly completed successfully.`
- `MASTER RUN COMPLETE`
- `backend/evaluation/results/` 아래 결과 JSON 5종 생성 확인
- `backend/evaluation/results/TABLES.md` 재생성 시각 확인
- 결과 값이 전부 동일 점수나 0 점수로 수렴하지 않는지 확인

## 현재 운영 기준

- 기본 생성 모델은 Base
- Mini 모델은 로컬 스모크 검증에서만 환경변수로 전환
- SQLAlchemy ORM은 유지하고 기본 DB는 PostgreSQL
- SQLite는 로컬 임시 점검 경로

## 실패 시 우선 확인

- stale `uvicorn api.main:app` 프로세스 존재 여부
- `JWT_SECRET_KEY` 와 `LOAD_GPU_MODELS` 설정 여부
- CUDA 인식 여부
- `backend/data/` 와 `backend/evaluation/data/` 입력 파일 존재 여부
- `backend/scripts/master_run.log` 의 마지막 성공 단계

## 다음 단계 후보

- 내일 로컬 완주 실행
- 결과 테이블 유효성 검토
- 필요 시 공개 배포용 문서 분리
- 삭제 후보 문서와 산출물 정리 여부를 사용자와 협의
