# M-RAG 최신 작업 계획

- 문서 기준 2026-04-26
- 목적 로컬 연구 실행 경로를 하나로 고정하고 결과 검증 기준을 명확히 유지

## 목표

- `backend/scripts/master_run.py` 기준으로 전체 실험 재실행 가능 상태 유지
- `backend/evaluation/results/TABLES.md` 를 최신 실행 결과로 재생성 가능 상태 유지
- 문서와 코드의 모델 정책을 Mini 기본값, Base 선택형으로 일치

## 표준 작업 순서

### 1 사전 정리

- Python 프로세스 중복 실행 여부 확인
- `:8000` 포트 점유 프로세스 확인
- GPU 메모리 상태 확인
- `.venv` 활성화

### 2 모델과 데이터 준비

- `python scripts/download_models.py`
- 실험 PDF가 이미 있으면 `--skip-download`
- 새 환경이면 `download_test_papers.py` 로 데이터 확보

### 3 전체 실험 실행

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
$env:LOAD_GPU_MODELS = "true"
python scripts\master_run.py --skip-download
```

### 4 결과 검증

- `backend/scripts/master_run.log` 에 `STEP 12`, `STEP 13`, `MASTER RUN COMPLETE` 확인
- `backend/evaluation/results/` 아래 결과 JSON 5종 생성 확인
- `backend/evaluation/results/TABLES.md` 재생성 시각 확인
- `/api/chat/query` 로그에서 실제 생성 지연이 있는지 확인
- 값이 전부 동일하거나 0으로 수렴하지 않는지 확인

## 현재 운영 기준

- 기본 생성 모델은 Mini
- Base 모델은 필요 시 환경변수로만 전환
- 양자화는 사용하지 않음
- 불필요 문서와 코드 삭제는 사용자 확인 후 진행

## 실패 시 우선 점검

- stale `uvicorn api.main:app` 프로세스 존재 여부
- `JWT_SECRET_KEY` 와 `LOAD_GPU_MODELS` 환경변수 누락 여부
- 토크나이저 캐시와 모델 캐시 손상 여부
- `backend/data/` 와 `backend/evaluation/data/` 의 입력 파일 존재 여부

## 다음 단계 후보

- 로컬 완주 실행
- 결과 테이블 품질 검토
- 필요 시 공개 배포용 문서 분리
- 삭제 후보 문서와 산출물 정리 여부를 사용자와 협의
