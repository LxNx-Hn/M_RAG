# M-RAG 테스트 가이드

- 기준일 2026-04-15
- 목적 로컬 검증 절차와 CI 절차 일치

## 1 로컬 사전 준비

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
pip install ruff black pytest
cd frontend && npm ci
```

## 2 백엔드 정적 검사

```bash
cd backend
python -m ruff check .
python -m black --check .
```

## 3 백엔드 테스트 실행 규칙

- `backend/tests/test_api.py`는 pytest 수집 대상 아님
- 통합 스모크는 직접 실행 방식 사용
- pytest는 단위 테스트 파일만 수집

```bash
cd backend
python -m pytest -q
```

```bash
cd backend
python -X utf8 tests/test_api.py
```

## 4 프론트엔드 검사

```bash
cd frontend
npm run lint
npm run build
```

## 5 도커 검증

```bash
cd backend
docker build -t mrag-backend-ci .

cd ../frontend
docker build -t mrag-frontend-ci .
```

## 6 CI 구성 체크포인트

- backend job
- frontend job
- docker build 단계
- GitHub Actions Node24 런타임 강제 변수 적용
- checkout setup-node setup-python 최신 메이저 사용

## 7 연구용 수동 시나리오

- 로그인 후 `/api/auth/me` 200 확인
- 토큰 없이 보호 라우트 호출 시 401 확인
- 문서 업로드 후 `/api/papers/list` 반영 확인
- `/api/chat/query` 응답의 route follow_ups 확인
- `/api/chat/query/stream` done 이벤트 수신 확인
- `/api/citations/list` `/api/citations/download` 응답 확인

## 8 실패 대응 우선순위

- 1순위 보안 관련 실패 인증 인가 데이터 격리
- 2순위 데이터 무결성 실패 업로드 삭제 롤백
- 3순위 스트리밍 안정성 실패 타임아웃 에러 프레임
- 4순위 문서 정합성 실패 README FEATURES GUIDE 불일치
