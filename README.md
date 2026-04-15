# M-RAG

- 문서 기준일 2026-04-15
- 문서 목적 현재 구현 기능과 실행 절차 안내
- 문서 원칙 마침표 없는 개조식

## 1 프로젝트 요약

- 학술 문서 기반 질의응답 시스템
- 문서 유형 자동 판별 `paper` `lecture` `patent` `general`
- 라우트 기반 파이프라인 A B C D E F
- CAD SCD 기반 생성 제어
- FastAPI + React + PostgreSQL + ChromaDB 구성

## 2 핵심 기능

- 문서 업로드 PDF DOCX TXT
- 하이브리드 검색 Dense BM25 RRF
- 인용 추적 arXiv 및 특허 번호 처리
- 참고문헌 목록 조회 다운로드 지원
- SSE 스트리밍 답변 및 follow_ups 전송
- 퀴즈 생성 Route F
- JWT 인증 로그아웃 토큰 무효화

상세 기능 문서  
- [FEATURES.md](docs/FEATURES.md)

## 3 빠른 시작

```bash
git clone <repo-url>
cd M_RAG
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
cd frontend && npm ci && cd ..
```

## 4 실행

개발 실행
```bash
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

```bash
cd frontend
npm run dev
```

도커 실행
```bash
docker compose up --build
```

접속
- 프론트 개발 `http://localhost:5173`
- 프론트 도커 `http://localhost:3000`
- 백엔드 문서 `http://localhost:8000/docs`
- 헬스체크 `http://localhost:8000/health`

## 5 테스트

정적 검사
```bash
cd backend
python -m ruff check .
python -m black --check .
```

단위 테스트
```bash
cd backend
python -m pytest -q
```

통합 스모크
```bash
cd backend
python -X utf8 tests/test_api.py
```

프론트 검사
```bash
cd frontend
npm run lint
npm run build
```

## 6 API 요약

- 인증 `/api/auth/register` `/api/auth/login` `/api/auth/logout` `/api/auth/me`
- 문서 `/api/papers/upload` `/api/papers/list` `/api/papers/{doc_id}` `/api/papers/{collection_name}`
- 채팅 `/api/chat/query` `/api/chat/query/stream` `/api/chat/search` `/api/chat/export/ppt`
- 인용 `/api/citations/list` `/api/citations/download` `/api/citations/track`
- 기록 `/api/history/conversations` `/api/history/conversations/{id}/messages`

## 7 문서 목록

- [WORK_PLAN.md](WORK_PLAN.md)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [CONCEPTS.md](docs/CONCEPTS.md)
- [DEPLOY.md](docs/DEPLOY.md)
- [TESTING_GUIDE.md](docs/GUIDE/TESTING_GUIDE.md)
- [GuideV2.md](docs/GUIDE/GuideV2.md)

## 8 운영 단계

- 연구용 사용 가능
- 내부 시연용 사용 가능
- 외부 공개용은 공개 전 필수 조건 완료 후 전환

운영 기준 문서  
- [PROD_AUDIT_FINAL_REPORT.md](docs/GUIDE/PROD_AUDIT_FINAL_REPORT.md)
