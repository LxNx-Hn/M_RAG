# M-RAG 사용법 문서

- 문서 기준 2026-04-26
- 실행, 검증, 운영에 바로 쓰는 문서를 모아둔 시작점

## 포함 문서

- `DEPLOY.md` 로컬 실행, Docker 실행, GPU 서버 실행
- `WORK_PLAN.md` 최신 실험 실행 계획
- `HANDOFF.md` 다음 세션 인수인계
- `POSTGRES_GUIDE.md` PostgreSQL 전환과 운영 기준
- `TESTING_GUIDE.md` 테스트와 스모크 검증 기준

## 기본 순서

- 먼저 `README.md` 에서 전체 구조 확인
- 실행은 `WORK_PLAN.md` 또는 `DEPLOY.md` 기준으로 진행
- 세션 재개가 필요하면 `HANDOFF.md` 확인
- DB 전환이 필요할 때만 `POSTGRES_GUIDE.md` 확인
- 테스트 기준은 `TESTING_GUIDE.md` 확인
