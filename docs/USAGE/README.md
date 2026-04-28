# M-RAG 사용법 문서

## 문서 역할

| 문서 | 목적 |
|---|---|
| `DEPLOY.md` | 로컬, Docker, GPU 서버 실행 기준 |
| `RUNPOD_A100_NO_SSH.md` | RunPod A100에서 웹 터미널로 실험 실행 |
| `ALICE_CLOUD_GUIDE.md` | Alice Cloud에서 실험 실행 |
| `POSTGRES_GUIDE.md` | PostgreSQL 운영 DB 사용 |
| `TESTING_GUIDE.md` | 로컬 검증과 CI 검증 |

## 실행 경로 선택

| 목적 | 추천 경로 |
|---|---|
| 논문 실험 빠른 실행 | SQLite + SQLAlchemy + MIDM Base |
| 로컬 스모크 확인 | SQLite + SQLAlchemy + MIDM Mini |
| 운영/서비스 시연 | PostgreSQL + SQLAlchemy + MIDM Base |
| RunPod A100 실험 | GHCR image 또는 git clone + SQLite |
| Alice Cloud 실험 | git clone + venv + SQLite |

## 중요한 기준

- 논문 기준 기본 모델은 MIDM Base
- Mini는 로컬 스모크 검증용
- 논문 실험 경로는 MIDM Base 직접 디코딩을 기준으로 함
- vLLM과 외부 LLM API는 별도 추론 최적화/서비스 비교 문서에서 다룸
- 논문 실험에서는 DB 엔진보다 동일한 실험 경로와 결과 재현성이 중요
