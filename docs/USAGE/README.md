# M-RAG 사용법 문서

## 현재 평가 입력 기준

- 현재 재평가의 기준 입력은 `backend/evaluation/data/track1_queries.json` 과 `backend/evaluation/data/track2_queries.json`
- pseudo ground truth는 `backend/evaluation/data/pseudo_gt_track1.json` 과 `backend/evaluation/data/pseudo_gt_track2.json` 으로 별도 생성
- `korquad_25.json` 과 번역 CRAG 정규화 결과는 보조 준비 자산이며, 현재 로컬 paper-grounded 재평가의 직접 입력으로는 사용하지 않음

- 문서 기준 2026-04-27
- 실행, 검증, 운영에 바로 쓰는 문서를 모아둔 시작점

## 포함 문서

- `DEPLOY.md` 로컬 실행, Docker 실행, GPU 서버 실행
- `RUNPOD_A100_NO_SSH.md` RunPod A100 무SSH 실행 절차
- `RUNPOD_A100_NO_SSH.md` 는 GHCR 컨테이너 Pull 방식 우선 절차 포함
- `backend/scripts/runpod_one_shot.sh` 원샷 실행 스크립트
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

## 경로 선택 기준

- 논문과 연구 검증이 목표면 현재 로컬 실행 경로를 유지
- 이 경로에서는 CAD와 SCD를 포함한 생성 제어를 유지하는 것이 우선
- 따라서 이번 구현에서는 plain generation 전환이나 외부 상용 LLM API 연동, `vLLM` 전환을 진행하지 않음
- 이유는 현재 연구 검증 범위가 CAD와 SCD 기반 생성 제어를 포함한 논문 경로이기 때문
- OpenAI 같은 외부 API 연결은 쉬운 편이지만 CAD와 SCD 유지에는 적합하지 않음
- `vLLM` 은 아직 미구현이며, plain generation 서빙은 비교적 단순하지만 CAD와 SCD 유지형 연동은 별도 연구 과제
- 서비스 배포가 목표면 plain generation 기반 외부 추론 서버 분리를 후속 경로로 검토 가능
- 현재 기본 운영 기준은 PostgreSQL + Base 모델이며, Mini는 로컬 스모크 검증에만 사용
