# M-RAG: Modular RAG Paper Review Agent

학술 논문 PDF를 업로드하고 **한국어 질의응답, 다중 논문 비교, 인용 논문 추적**을 수행하는 Modular RAG 기반 챗봇 에이전트입니다.

쿼리 유형에 따라 파이프라인이 동적으로 변경되는 진정한 Modular RAG이며, **Context-Aware Contrastive Decoding(CAD)** 기반 환각 억제 모듈을 포함합니다.

---

## 핵심 특징

| 기능 | 설명 |
|---|---|
| **섹션 인식 청킹** | Abstract / Method / Result / Conclusion 구조 인식 |
| **동적 쿼리 라우터** | 질의 유형에 따라 6개 파이프라인 자동 선택 |
| **크로스링구얼 검색** | BGE-M3 한영 동시 처리, 한국어 질의 → 영어 논문 검색 |
| **하이브리드 검색** | Dense(BGE-M3) + Sparse(BM25) + RRF 결합 |
| **인용 논문 추적** | arXiv API 기반 Reference 논문 자동 수집 및 인덱싱 |
| **CAD 환각 억제** | 학습 없이 LogitsProcessor로 파라메트릭 지식 억제 |
| **RAGAS 평가** | Faithfulness, Answer Relevancy 등 4대 지표 자동 평가 |
| **React 프론트엔드** | 3패널 레이아웃, PDF 뷰어, 실시간 채팅, 다크모드 |
| **JWT 인증** | 회원가입/로그인, 대화 기록 DB 저장 |
| **다국어(i18n)** | 한국어/영어 실시간 전환 |

---

## 데모 UI

**React + TailwindCSS** 기반 3패널 인터페이스:

```
┌─────────┬──────────────────┬──────────┐
│  소스   │    PDF 뷰어      │   채팅   │
│  패널   │                  │   패널   │
│         │  하이라이트 지원  │          │
│ 업로드  │  줌/페이지 이동   │ 스트리밍 │
│ 논문목록 │                  │ 추천질문 │
└─────────┴──────────────────┴──────────┘
```

- **좌측 패널**: PDF/DOCX 업로드 + 논문 카드 (섹션 태그 표시)
- **중앙**: PDF 뷰어 + 출처 하이라이트 (하늘색)
- **우측**: 채팅 — 실시간 SSE 스트리밍 + 파이프라인 배지 + 출처 표시
- **토글 버튼**: 소스/채팅 패널 균형있는 토글
- **설정**: 다크모드, 한/영 전환, CAD ON/OFF, α 강도

---

## 쿼리 경로 (6개 파이프라인)

| 경로 | 트리거 예시 | 파이프라인 |
|---|---|---|
| A. 단순 QA | "이 논문에서 사용한 데이터셋이 뭐야?" | HyDE → 하이브리드 검색 → 재랭킹 → 생성 |
| B. 섹션 특화 | "결과가 어떻게 나왔어?" | 섹션 필터 검색 → boost 재랭킹 → 생성 |
| C. 멀티 비교 | "논문 A랑 B 비교해줘" | 병렬 검색 → 합성 → 비교 표 생성 |
| D. 인용 추적 | "인용 논문 분석해줘" | arXiv 수집 → 인덱싱 → 확장 검색 → 생성 |
| E. 전체 요약 | "이 논문 요약해줘" | 섹션별 검색 → 구조화 요약 생성 |
| F. 퀴즈 생성 | "이 내용으로 5문제 만들어줘" | 하이브리드 검색 → CAD 강제 → 객관식 생성 |

---

## 기술 스택

| 구분 | 기술 | 역할 |
|---|---|---|
| **프론트엔드** | **React + TailwindCSS + Zustand** | **3패널 SPA, SSE 스트리밍** |
| **백엔드** | **FastAPI** | **프로덕션 API 서버 (다중 사용자)** |
| PDF 파싱 | pymupdf | 블록 단위 추출 + 레이아웃 보존 |
| DOCX 파싱 | python-docx | Word 문서 지원 |
| 임베딩 | BGE-M3 | 한영 크로스링구얼 임베딩 (1024D) |
| 벡터DB | ChromaDB | 로컬 persistent, 메타데이터 필터링 |
| 생성 모델 | MIDM-2.0-Base-Instruct (11.5B) | 한국어 특화 오픈소스 LLM |
| 환각 억제 | Contrastive Decoding | 학습 없이 LogitsProcessor로 구현 |
| 재랭킹 | Cross-Encoder | ms-marco-MiniLM-L-6-v2 |
| 인증 | JWT + PostgreSQL | 회원가입/로그인, 대화 기록 저장 |
| 평가 | RAGAS | RAG 특화 자동 평가 (4대 지표) |
| 컨테이너 | Docker Compose | 3서비스 (DB + Backend + Frontend) |

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                     클라이언트                           │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │  React SPA   │  │   모바일 앱   │                     │
│  │   :5173      │  │    (PWA)     │                     │
│  └──────┬───────┘  └──────┬───────┘                     │
│         │                 │                             │
│         └─────────────────┘                             │
│                           │ HTTP/REST + SSE             │
│         ┌─────────────────▼─────────────────────┐       │
│         │      FastAPI 백엔드 API (:8000)        │       │
│         │  /api/papers  /api/chat  /api/auth     │       │
│         │  CORS · JWT · Async · Swagger Docs     │       │
│         └─────────────────┬─────────────────────┘       │
│                           │                             │
│         ┌─────────────────▼─────────────────────┐       │
│         │         RAG 모듈 레이어 (14개)         │       │
│         │  PDF→임베딩→검색→재랭킹→생성→CAD        │       │
│         └───────────────────────────────────────┘       │
│                           │                             │
│         ┌─────────────────▼─────────────────────┐       │
│         │            데이터 레이어               │       │
│         │  ChromaDB · PostgreSQL · File Storage   │       │
│         └───────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

## 빠른 시작

### 1. 설치

```bash
git clone <repo-url>
cd M_RAG

# 백엔드
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
cd ..

# 프론트엔드
cd frontend
npm install
npm run build
cd ..
```

### 2. 실행

```bash
# 방법 1: 백엔드 + 프론트엔드 분리 (개발)
cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000  # 터미널 1
cd frontend && npm run dev                                       # 터미널 2

# 방법 2: Docker Compose (프로덕션)
docker compose up --build

# 방법 3: 백엔드만 (API 테스트)
cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000
# → http://localhost:8000/docs (Swagger UI)
```

### 3. 접속

| 환경 | URL |
|---|---|
| React 프론트엔드 (개발) | http://localhost:5173 |
| React 프론트엔드 (Docker) | http://localhost:3000 |
| FastAPI Swagger | http://localhost:8000/docs |
| 헬스체크 | http://localhost:8000/health |

> GPU(24GB+ VRAM)가 없어도 검색/재랭킹까지 동작합니다. 생성(LLM)만 비활성화됩니다.

### 4. 테스트

```bash
# API 서버 실행 상태에서
cd backend && python -X utf8 tests/test_api.py
# → 23/23 PASS
```

---

## API 엔드포인트

### 핵심 API

| Method | Path | 설명 |
|---|---|---|
| `GET` | `/health` | 시스템 상태 (GPU, 컬렉션) |
| `POST` | `/api/papers/upload` | PDF/DOCX 업로드 → 파싱 → 인덱싱 |
| `GET` | `/api/papers/list` | 컬렉션 목록 |
| `DELETE` | `/api/papers/{name}` | 컬렉션 삭제 |
| `POST` | `/api/chat/query` | 질의응답 (전체 RAG 파이프라인) |
| `POST` | `/api/chat/query/stream` | SSE 스트리밍 질의응답 |
| `POST` | `/api/chat/search` | 검색만 (생성 없이) |
| `POST` | `/api/citations/track` | 인용 논문 추적 |

### 인증 API

| Method | Path | 설명 |
|---|---|---|
| `POST` | `/api/auth/register` | 회원가입 |
| `POST` | `/api/auth/login` | 로그인 (JWT 발급) |
| `GET` | `/api/auth/me` | 현재 사용자 정보 |

### 대화 기록 API

| Method | Path | 설명 |
|---|---|---|
| `GET` | `/api/history/conversations` | 대화 목록 |
| `POST` | `/api/history/conversations` | 새 대화 |
| `GET` | `/api/history/conversations/{id}/messages` | 메시지 조회 |
| `DELETE` | `/api/history/conversations/{id}` | 대화 삭제 |

---

## 프로젝트 구조

```
M_RAG/
├── backend/                      # Python 백엔드
│   ├── api/                      #   FastAPI 서버
│   │   ├── main.py               #     앱 진입점 + CORS + lifespan
│   │   ├── dependencies.py       #     모듈 싱글턴 관리
│   │   ├── schemas.py            #     Pydantic 요청/응답 스키마
│   │   ├── auth.py               #     JWT 인증 유틸리티
│   │   ├── database.py           #     SQLAlchemy DB 연결
│   │   ├── models.py             #     ORM 모델 (User, Conversation, Message)
│   │   └── routers/
│   │       ├── papers.py         #     /api/papers — 문서 관리
│   │       ├── chat.py           #     /api/chat — 질의응답 + SSE
│   │       ├── citations.py      #     /api/citations — 인용 추적
│   │       ├── auth.py           #     /api/auth — 인증
│   │       └── history.py        #     /api/history — 대화 기록
│   ├── modules/                  #   RAG 모듈 (14개)
│   │   ├── pdf_parser.py         #     MODULE 1: PDF 파싱
│   │   ├── section_detector.py   #     MODULE 2: 섹션 인식
│   │   ├── chunker.py            #     MODULE 3: 섹션/RAPTOR/명제 청킹
│   │   ├── embedder.py           #     MODULE 4: BGE-M3 임베딩
│   │   ├── vector_store.py       #     MODULE 5: ChromaDB 관리
│   │   ├── query_router.py       #     MODULE 6: 쿼리 라우터
│   │   ├── query_expander.py     #     MODULE 7: HyDE + 다중 쿼리
│   │   ├── hybrid_retriever.py   #     MODULE 8: BM25 + Dense + RRF
│   │   ├── reranker.py           #     MODULE 9: Cross-Encoder 재랭킹
│   │   ├── context_compressor.py #     MODULE 10: 컨텍스트 압축
│   │   ├── citation_tracker.py   #     MODULE 11: 인용 추적 + arXiv
│   │   ├── generator.py          #     MODULE 12: MIDM-2.0 생성 + 스트리밍
│   │   ├── cad_decoder.py         #     MODULE 13A: CAD 환각 억제
│   │   ├── scd_decoder.py         #     MODULE 13B: SCD 언어 이탈 방지
│   │   ├── followup_generator.py  #     추천 질문 생성
│   │   ├── patent_tracker.py      #     특허 인용/유사 특허 추적
│   │   └── docx_parser.py         #     DOCX/TXT 파싱
│   ├── pipelines/                #   동적 파이프라인 (6개)
│   │   ├── pipeline_a_simple_qa.py
│   │   ├── pipeline_b_section.py
│   │   ├── pipeline_c_compare.py
│   │   ├── pipeline_d_citation.py
│   │   ├── pipeline_e_summary.py
│   │   └── pipeline_f_quiz.py
│   ├── evaluation/               #   평가 프레임워크
│   │   ├── ragas_eval.py
│   │   ├── ablation_study.py
│   │   └── test_queries.json
│   ├── tests/
│   │   └── test_api.py           #   API 통합 테스트 (23개)
│   ├── config.py                 #   전역 설정
│   ├── requirements.txt          #   Python 의존성
│   └── Dockerfile                #   백엔드 Docker
├── frontend/                     # React 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/           #   3패널 레이아웃 + TopBar
│   │   │   ├── source/           #   소스 패널 (업로드, 논문목록)
│   │   │   ├── viewer/           #   PDF 뷰어 + 하이라이트
│   │   │   ├── chat/             #   채팅 (메시지, 스트리밍, 라우트배지)
│   │   │   ├── auth/             #   로그인/회원가입
│   │   │   └── history/          #   대화 기록
│   │   ├── stores/               #   Zustand 상태 관리
│   │   ├── api/                  #   API 클라이언트 (Axios + SSE)
│   │   ├── i18n/                 #   한/영 다국어
│   │   └── types/                #   TypeScript 타입
│   ├── Dockerfile                #   프론트엔드 Docker (Nginx)
│   └── nginx.conf                #   Nginx SPA + 프록시
├── docs/                         # 문서
│   ├── CONCEPTS.md               #   초보자용 개념 설명
│   ├── DEPLOY.md                 #   배포 가이드
│   ├── ARCHITECTURE.md           #   아키텍처 문서
│   └── Guide.md                  #   사용 가이드
├── docker-compose.yml            # 3서비스 Compose
└── README.md                     # 프로젝트 개요
```

---

## 핵심 알고리즘

### Context-Aware Contrastive Decoding (CAD)

```
Logit_final = Logit(문서 포함 프롬프트) - α × Logit(문서 없는 프롬프트)
```

모델이 다음 토큰을 예측할 때 파라메트릭 지식(사전 학습 기억)의 개입을 실시간으로 억제합니다. 파인튜닝 없이 `LogitsProcessor` 하나로 구현됩니다.

### Reciprocal Rank Fusion (RRF)

```
RRF_score(d) = Σ weight_i / (k + rank_i(d))
```

Dense 검색(의미)과 Sparse 검색(키워드)의 결과를 통합합니다.

---

## Docker 배포

```bash
# GPU 모델 활성화
LOAD_GPU_MODELS=true docker compose up --build

# CPU 전용 (검색/재랭킹만)
docker compose up --build

# 서비스 구성
#   - db (PostgreSQL :5432)
#   - backend (FastAPI :8000)
#   - frontend (Nginx :3000)
```

자세한 내용은 [DEPLOY.md](docs/DEPLOY.md) 참조.

---

## 평가

### Ablation Study (6단계)

| # | 시스템 | 누적 모듈 |
|---|---|---|
| 1 | Naive RAG | 고정 청킹 + 벡터 검색 + 생성 |
| 2 | + Section Chunking | 섹션 인식 청킹 |
| 3 | + Hybrid Search | BM25 + Dense + RRF |
| 4 | + Reranker | Cross-Encoder 재랭킹 |
| 5 | + Router + HyDE | 동적 라우팅 + HyDE |
| 6 | **Full System** | + CAD + 압축 |

---

## 문서

| 문서 | 설명 |
|---|---|
| [README.md](README.md) | 프로젝트 개요 (이 문서) |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 모듈 의존성, 데이터 흐름, 알고리즘 |
| [DEPLOY.md](docs/DEPLOY.md) | 배포 가이드 (Docker, Nginx, RunPod) |
| [CONCEPTS.md](docs/CONCEPTS.md) | 초보자용 개념 설명 (RAG, LLM, vLLM 등) |

---

## 참고 논문

- Gao et al. (2023) — RAG Survey, ICLR 2024
- Chen et al. (2024) — BGE M3-Embedding, ACL 2024
- Shi et al. (2023) — Context-Aware Decoding, NAACL 2024
- Sarthi et al. (2024) — RAPTOR, ICLR 2024
- Gao et al. (2022) — HyDE, ACL 2023
- Es et al. (2023) — RAGAS, EACL 2024

---

## 라이선스

이 프로젝트는 졸업작품 및 포트폴리오 목적으로 개발되었습니다.
