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
cd backend
python -m pytest -q
```

`backend/tests/test_api.py`는 API 통합 스모크 성격이 강하다. 보호 라우트는 bearer token이 필요하므로 스크립트 내부 토큰 생성 경로를 확인하고 실행한다.

```bash
cd backend
python -X utf8 tests/test_api.py
```

## Frontend 검사

```bash
cd frontend
npm run lint
npm run build
```

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
