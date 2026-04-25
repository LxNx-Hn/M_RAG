# M-RAG

- 문서 기준 2026-04-26
- 현재 기준 로컬 연구용 실험과 시연용 실행 경로를 반영한 메인 문서
- 패키지 표식용 `__init__.py` 는 역할이 단순해 코드 맵에서 생략

## 프로젝트 개요

- 한국어 중심 학술 문서 질의응답과 환각 억제를 위한 Modular RAG 시스템
- FastAPI 백엔드와 React 프론트엔드로 구성
- 논문 업로드, 하이브리드 검색, 라우팅 기반 파이프라인, 인용 추적, 퀴즈 생성 지원
- 로컬 연구 실행 기본 모델은 `K-intelligence/Midm-2.0-Mini-Instruct`
- `K-intelligence/Midm-2.0-Base-Instruct` 도 유지하되 환경변수로 명시적으로 선택
- 양자화 경로는 현재 사용하지 않음

## 표준 실행 경로

### 1 환경 준비

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend\requirements.txt
cd frontend
npm ci
cd ..
```

- 여러 Python 환경이 섞여 있으면 `python` 대신 `.venv\Scripts\python.exe` 사용 권장
- 로컬 기본 DB는 SQLAlchemy가 여는 `backend/mrag.db` SQLite 파일
- PostgreSQL을 쓰려면 `DATABASE_URL` 환경변수로 별도 지정

### 2 모델 캐시 준비

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
python scripts\download_models.py
```

- 기본값은 `backend/config.py` 의 `GENERATION_MODEL`
- Base 모델을 미리 캐시할 때만 아래처럼 명시

```powershell
python scripts\download_models.py --llm-model K-intelligence/Midm-2.0-Base-Instruct
```

### 3 전체 실험 실행

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
$env:JWT_SECRET_KEY = "change-this-secret"
$env:LOAD_GPU_MODELS = "true"
python scripts\master_run.py --skip-download
```

- 이미 준비된 PDF를 그대로 사용하면 `--skip-download`
- API 서버를 별도로 띄운 상태면 `--skip-server`
- 표준 성공 기준은 `backend/scripts/master_run.log` 의 아래 세 줄
  - `STEP 12 - Validate results completed successfully.`
  - `STEP 13 - Stop the API server subprocess cleanly completed successfully.`
  - `MASTER RUN COMPLETE`

### 4 개발 서버 실행

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\backend
$env:JWT_SECRET_KEY = "change-this-secret"
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG\frontend
npm run dev
```

## 모델 운영 기준

- 기본 로컬 실험 모델은 Mini
- Base 모델은 `GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct` 로만 선택
- Mini와 Base 모두 `bfloat16 + device_map=auto` 로 로드
- 현재 저장소에는 4-bit 양자화와 `bitsandbytes` 의존 경로를 두지 않음
- 로컬 12GB급 GPU는 Mini 기준으로 운영
- 24GB 이상 GPU가 있을 때만 Base 사용 권장

## 연구 경로와 서비스 경로

- 논문 목표 경로는 현재 구조를 그대로 유지
- 이 경로에서는 CAD와 SCD를 포함한 생성 제어가 핵심
- 따라서 이번 구현에서는 plain generation 전환이나 외부 상용 LLM API 전환, `vLLM` 전환을 진행하지 않음
- 이유는 현재 논문 클레임이 CAD와 SCD 기반 환각 억제와 언어 이탈 억제에 있기 때문
- OpenAI 같은 외부 API 연결은 상대적으로 쉬운 편이지만 CAD와 SCD를 그대로 유지하기는 어려움
- `vLLM` 은 아직 구현되어 있지 않으며, plain generation 서빙은 비교적 단순하지만 CAD와 SCD 유지형 연동은 추가 연구와 구현이 필요
- 서비스 배포 목표에서는 plain generation 기반 외부 추론 서버 분리를 후속 선택지로 검토 가능
- `vLLM` 기반 RAG에서 환각 억제 기법을 유지하는 연구는 다음 단계 클레임 후보로 분리

## 주요 결과물 경로

- 실험 결과 JSON `backend/evaluation/results/*.json`
- 마크다운 요약 표 `backend/evaluation/results/TABLES.md`
- 자동 실행 로그 `backend/scripts/master_run.log`
- 업로드 문서와 실험 PDF `backend/data/`
- 벡터 저장소 `backend/chroma_db/`

## 코드 맵

### Backend API

- `backend/api/main.py` FastAPI 진입점, lifespan 초기화, 전역 로깅, CORS, 보안 헤더, 예외 처리
- `backend/api/auth.py` JWT 생성과 검증, 비밀번호 해시, 현재 사용자 식별 의존성
- `backend/api/database.py` SQLAlchemy 엔진과 세션, DB 초기화
- `backend/api/dependencies.py` RAG 모듈 싱글턴 초기화와 공유
- `backend/api/limiter.py` `slowapi` 기반 레이트 리밋 설정
- `backend/api/models.py` `User`, `Conversation`, `Message`, `Paper`, `RevokedToken` ORM 모델
- `backend/api/schemas.py` 요청과 응답 Pydantic 스키마
- `backend/api/routers/auth.py` 회원가입, 로그인, 로그아웃, 현재 사용자 조회
- `backend/api/routers/papers.py` 업로드, 목록, 상세, 삭제, 파일 검증과 사용자 격리
- `backend/api/routers/chat.py` 검색, 답변 생성, SSE 스트리밍, PPT 내보내기
- `backend/api/routers/citations.py` 인용 목록, 다운로드, 추적 API
- `backend/api/routers/history.py` 대화 생성, 메시지 저장, 대화 삭제와 사용자별 조회

### Backend Modules

- `backend/modules/pdf_parser.py` PDF 텍스트와 메타데이터 추출
- `backend/modules/docx_parser.py` DOCX와 TXT 텍스트 추출
- `backend/modules/section_detector.py` 문서 유형과 섹션 타입 감지
- `backend/modules/chunker.py` 섹션 기반 청킹과 RAPTOR 계층 청킹
- `backend/modules/embedder.py` `BAAI/bge-m3` 임베딩 생성
- `backend/modules/vector_store.py` ChromaDB 컬렉션 저장, 조회, 삭제
- `backend/modules/query_router.py` 질문 의도 분석과 A~F 라우팅 결정
- `backend/modules/query_expander.py` HyDE, 다중 질의 확장, 언어 보조 확장
- `backend/modules/hybrid_retriever.py` Dense와 BM25 결합 검색, RRF 융합
- `backend/modules/reranker.py` Cross-Encoder 재정렬과 섹션 가중치 보정
- `backend/modules/context_compressor.py` 검색 컨텍스트 압축과 토큰 예산 조절
- `backend/modules/generator.py` MIDM Mini 또는 Base 기반 답변 생성과 스트리밍
- `backend/modules/cad_decoder.py` CAD 기반 환각 억제 로짓 보정
- `backend/modules/scd_decoder.py` SCD 기반 언어 이탈 억제 로짓 보정
- `backend/modules/citation_tracker.py` 참고문헌 파싱과 arXiv 기반 추적
- `backend/modules/patent_tracker.py` 특허 식별자 파싱과 Google Patents 연동
- `backend/modules/followup_generator.py` 후속 질문 후보 생성
- `backend/modules/pptx_exporter.py` 채팅 결과의 PPTX 변환

### Backend Pipelines

- `backend/pipelines/pipeline_a_simple_qa.py` 기본 QA 파이프라인
- `backend/pipelines/pipeline_b_section.py` 섹션 필터 기반 QA 파이프라인
- `backend/pipelines/pipeline_c_compare.py` 다중 문서 비교 파이프라인
- `backend/pipelines/pipeline_d_citation.py` 인용 추적 파이프라인
- `backend/pipelines/pipeline_e_summary.py` 전체 요약 파이프라인
- `backend/pipelines/pipeline_f_quiz.py` 퀴즈와 플래시카드 생성 파이프라인

### Backend Evaluation

- `backend/evaluation/ablation_study.py` 모듈별 ablation 실험 로직
- `backend/evaluation/decoder_ablation.py` CAD와 SCD 실험 로직
- `backend/evaluation/ragas_eval.py` RAGAS 평가와 휴리스틱 폴백
- `backend/evaluation/run_track1.py` Track 1 실행기
- `backend/evaluation/run_track2.py` Track 2 실행기
- `backend/evaluation/test_queries.json` 기본 실험 질의 세트
- `backend/evaluation/data/korquad_25.json` KorQuAD 샘플 쿼리
- `backend/evaluation/data/crag_ko_25.json` CRAG 기반 한국어 샘플 쿼리
- `backend/evaluation/data/pseudo_gt.json` pseudo ground truth 저장
- `backend/evaluation/data/track1_queries.json` Track 1 통합 질의 세트
- `backend/evaluation/data/track2_queries.json` Track 2 통합 질의 세트

### Backend Scripts

- `backend/scripts/master_run.py` 전체 실험 자동 실행, 서버 기동, 결과 검증, 안전 종료
- `backend/scripts/download_models.py` 임베딩, 리랭커, 선택한 LLM 사전 캐시
- `backend/scripts/download_test_papers.py` 실험용 PDF 다운로드
- `backend/scripts/index_papers.py` 실험용 문서를 API로 일괄 업로드
- `backend/scripts/generate_pseudo_gt.py` pseudo ground truth 생성
- `backend/scripts/prepare_korquad.py` KorQuAD 샘플링
- `backend/scripts/prepare_crag.py` CRAG 샘플링과 변환
- `backend/scripts/results_to_markdown.py` 결과 JSON을 `TABLES.md` 로 변환
- `backend/scripts/experiments/run_all_experiments.py` 단일 논문 기준 레거시 실험 실행기
- `backend/scripts/experiments/run_c3_experiment.py` C3 관련 별도 실험 실행기
- `backend/scripts/verify_deployment.py` 배포 환경 체크
- `backend/scripts/experiments/runpod_experiment.sh` RunPod 실험 보조 스크립트
- `backend/scripts/experiments/README.md` 보존형 실험 스크립트 묶음 설명
- `backend/scripts/backup.sh` Postgres, Chroma, data 백업
- `backend/scripts/entrypoint.sh` 컨테이너 엔트리포인트와 마이그레이션 실행

### Frontend App

- `frontend/src/main.tsx` React 부트스트랩
- `frontend/src/App.tsx` 인증 상태에 따른 앱 진입 분기
- `frontend/src/index.css` 전역 스타일과 테마 변수
- `frontend/src/api/client.ts` Axios 인스턴스와 401 공통 처리
- `frontend/src/api/chat.ts` 채팅과 검색 API 호출
- `frontend/src/api/papers.ts` 문서 API 호출
- `frontend/src/api/citations.ts` 인용 API 호출
- `frontend/src/stores/authStore.ts` 인증 상태와 개발용 skip auth 상태
- `frontend/src/stores/chatStore.ts` 메시지, 스트리밍, 검색 상태
- `frontend/src/stores/paperStore.ts` 업로드 문서와 선택 상태
- `frontend/src/stores/uiStore.ts` 레이아웃과 다크모드 상태
- `frontend/src/components/layout/AppLayout.tsx` 메인 3열 레이아웃 조립
- `frontend/src/components/layout/TopBar.tsx` 상단 바와 전역 액션
- `frontend/src/components/auth/LoginPage.tsx` 로그인과 회원가입 화면
- `frontend/src/components/source/SourcePanel.tsx` 업로드 문서 목록과 소스 패널
- `frontend/src/components/chat/ChatPanel.tsx` 채팅 입력, 응답, 스트리밍 렌더링
- `frontend/src/components/chat/MessageBubble.tsx` 개별 메시지 UI
- `frontend/src/components/chat/RouteBadge.tsx` 파이프라인 배지 표시
- `frontend/src/components/chat/FlashcardViewer.tsx` 퀴즈와 플래시카드 표시
- `frontend/src/components/history/ConversationList.tsx` 대화 이력 목록
- `frontend/src/components/viewer/PDFViewer.tsx` PDF 본문 렌더링
- `frontend/src/components/viewer/HighlightLayer.tsx` 인용 하이라이트 오버레이
- `frontend/src/components/viewer/CitationPanel.tsx` 인용 상세 패널
- `frontend/src/types/api.ts` API 응답 타입
- `frontend/src/types/chat.ts` 채팅 데이터 타입
- `frontend/src/types/paper.ts` 문서 데이터 타입
- `frontend/src/utils/export.ts` 프론트 내보내기 보조 유틸
- `frontend/src/i18n/index.ts` 국제화 설정

### 산출물과 세션 메모

- `backend/evaluation/results/` 아래 파일은 실행 결과 산출물
- `docs/USAGE/HANDOFF.md` 는 다음 세션 인수인계용 최신 문서
- 불필요 문서와 코드 삭제는 사용자 확인 후 진행

## 문서 맵

### 루트 문서

- `README.md` 프로젝트 개요, 실행 경로, 코드 맵을 보는 시작점

### 사용법 문서

- `docs/USAGE/README.md` 사용법 문서 묶음 시작점
- `docs/USAGE/DEPLOY.md` 로컬 실행, Docker 실행, GPU 서버 실행 방법
- `docs/USAGE/WORK_PLAN.md` 최신 실험 실행 계획
- `docs/USAGE/HANDOFF.md` 세션 재개용 인수인계 문서
- `docs/USAGE/POSTGRES_GUIDE.md` PostgreSQL 전환과 운영 기준
- `docs/USAGE/TESTING_GUIDE.md` 테스트와 스모크 검증 기준

### 구조 문서

- `docs/ARCHITECTURE.md` 계층 구조와 요청 흐름
- `docs/FEATURES.md` 현재 제공 기능 범위

### 논문 문서

- `docs/PAPER/README.md` 논문 문서 묶음 시작점
- `docs/PAPER/GUIDE_ORIGINAL.md` 과거 국문 논문 원본 초안 복구본
- `docs/PAPER/THESIS.md` 제출용 논문 본문 초안
- `docs/GUIDE/GuideV2.md` 논문 본문 작성 기준서
- `docs/PAPER/ACADEMIC_CLAIMS.md` 주장 가능한 기여와 근거 파일
- `docs/PAPER/COMPETITIVE_ANALYSIS.md` 비교 포지셔닝 초안
- `docs/PAPER/LIMITATIONS_AND_FUTURE_WORK.md` 한계와 후속 과제

### 발표용 문서

- `docs/PRESENTATION/README.md` 발표용 문서 묶음 시작점
- `docs/PRESENTATION/SUMMARY.md` 발표용 요약 문서
- `docs/PRESENTATION/CONCEPTS.md` 개념 용어집
- `docs/PRESENTATION/EXPLAINED.md` 비전공자용 설명 문서

## 운영 메모

- 로컬 연구 실행은 `backend/scripts/master_run.py` 를 기준으로 유지
- 로컬 기본 영속 계층은 SQLAlchemy + SQLite, PostgreSQL은 운영과 확장 경로로 사용
- 문서와 코드에서 양자화 경로를 다시 넣지 않음
- Base 모델은 유지하지만 기본값으로 강제하지 않음
- 삭제 후보가 보여도 사용자 확인 전에는 제거하지 않음
