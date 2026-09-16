# M-RAG 테스트 가이드

## 목적

로컬 검증과 CI 검증 절차를 정리한다.

## Backend 정적 검사

```bash
cd backend
python -m ruff check .
python -m black --check .
```

## Backend 테스트

```bash
python -m pytest tests/backend -q
```

`tests/backend/test_api.py`는 API 통합 스모크 성격이 강하다. 보호 라우트는 bearer token이 필요하므로 스크립트 내부 토큰 생성 경로를 확인하고 실행한다.

```bash
python -X utf8 tests/backend/test_api.py
```

## Frontend 검사

```bash
cd frontend
npm run lint
npm run build
```

## 최종 논문 패키지 검증

제출용 논문 내용, 표·그림, UI 재현 화면, 주장-근거 연결은 `FINALDOCS/`에만
둔다. 아래 검증은 저장된 파일만 읽으며 네트워크, 모델, retrieval, generation,
judge 호출 또는 결과 파일 쓰기를 하지 않는다.

```powershell
python -X utf8 FINALDOCS\VALIDATION\verify_finaldocs_60q.py
```

- 현재 원고는 60개 한국어 질의와 8개 configuration의 480개 저장 generation
  record를 사용한다.
- HyDE·CAD·SCD의 주장 범위와 수치 근거는
  `FINALDOCS/VALIDATION/FINAL_CLAIM_MAP_60Q.md`로 확인한다.

## Offline evidence replay

```bash
python -X utf8 cli/evidence_replay.py list
python -X utf8 cli/evidence_replay.py show E03
python -X utf8 cli/evidence_replay.py inspect track1_0009
```

This viewer reads artifacts only; it performs no retrieval, generation, judge
call, database connection, or write to `experiments/results/`.

## Docker build 확인

```bash
cd backend
docker build -t mrag-backend-ci .
```

```bash
cd frontend
docker build -t mrag-frontend-ci .
```

## 수동 API 체크

- `/health` 200 확인
- 토큰 없이 보호 라우트 401 확인
- 로그인 후 `/api/auth/me` 확인
- 문서 업로드 확인
- `/api/chat/search` 검색 결과 확인
- `/api/chat/query` 답변과 follow_ups 확인
- `/api/chat/query/stream` done 이벤트 확인
- `/api/chat/judge` label 판정 확인
- `/api/chat/export/ppt` PPTX 반환 확인
